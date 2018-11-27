## Copyright (c) 2015 SONATA-NFV, 2017 5GTANGO [, ANY ADDITIONAL AFFILIATION]
## ALL RIGHTS RESERVED.
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
## Neither the name of the SONATA-NFV, 5GTANGO [, ANY ADDITIONAL AFFILIATION]
## nor the names of its contributors may be used to endorse or promote
## products derived from this software without specific prior written
## permission.
##
## This work has been performed in the framework of the SONATA project,
## funded by the European Commission under Grant number 671517 through
## the Horizon 2020 and 5G-PPP programmes. The authors would like to
## acknowledge the contributions of their colleagues of the SONATA
## partner consortium (www.sonata-nfv.eu).
##
## This work has been performed in the framework of the 5GTANGO project,
## funded by the European Commission under Grant number 761493 through
## the Horizon 2020 and 5G-PPP programmes. The authors would like to
## acknowledge the contributions of their colleagues of the 5GTANGO
## partner consortium (www.5gtango.eu).

import pandas as pd
import os
import json
import database.db_connect as mongo_db
import methods.main_methods as meth
import logmatic
import logging
import warnings
import matplotlib.pyplot as plt
from classes.JsonEncoder import JSONEncoder as json_enc
from flask import Flask,request,render_template,Response
from fileinput import filename
from numpy.ma import extras

app = Flask(__name__)

UPLOAD_DADA_FOLDER = 'data'
warnings.filterwarnings("ignore", module="matplotlib")

cat_url = os.environ['CATALOGUES_URL']
db_host = os.environ['DATABASE_HOST']
db_port = os.environ['DATABASE_PORT']
db_name = os.environ['DATABASE_NAME']
dict_coll = os.environ['DICT_COLL']
enc_fig_coll = os.environ['ENC_FIGS_COLL']
unk_vnf_coll = os.environ['UNK_COLL']
log_level = os.environ['LOG_LEVEL']


# cat_url  = "http://pre-int-sp-ath.5gtango.eu:4011/catalogues/api/v2/"
# db_host = "mongo"
# db_port = 27017
# db_name = "tng-sdk-analyze-weight"
# dict_coll = "dictionaries"
# unk_vnf_coll = "unknown_vnfs"
# enc_fig_coll = "encoded_figs"
# log_level = "INFO"

logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(logmatic.JsonFormatter(extra={"hostname":"tng-sdk-analyze-weight"}))
logger.addHandler(handler)
level = logging.getLevelName(log_level)
enc_fig_coll = "encoded_figs"
logger.setLevel(level)

# Create a URL route in our application for "/"
@app.route('/tng-sdk-analyze-weight/api/weight/v1')
def home():
    logger.info("Logging home end point")
    return render_template('home.html')

# Create a URL route in our application for "/"
@app.route('/tng-sdk-analyze-weight/api/weight/v1/mgmt/fig/<vnf_type>')
def generate_fig_html(vnf_type):
    logger.info("Logging Generating figure in html")
    response = mongo_db.get_fig_base64(db_name, enc_fig_coll, vnf_type)
    return render_template(response)

@app.route('/tng-sdk-analyze-weight/api/weight/v1/train', methods=['GET'])
def train():
    logger.warning("Logging training end point")
    mongo_db.drop_collection(db_name, dict_coll)
    mongo_db.drop_collection(db_name, enc_fig_coll)
    logger.info("Call in mongo container")
    for root, dirs, files in os.walk(UPLOAD_DADA_FOLDER):
        for filename in files:     
            try:
                d = pd.read_csv(UPLOAD_DADA_FOLDER+"/"+filename, index_col=0)
                meth.fig_to_base64(d, filename[:-4])
            except IOError as e:
                logging.error('An error occured', extra={"error": e})               
            df = pd.DataFrame(data = d)
            result = meth.get_top_abs_correlations(df, 5) 
            json_result = json.loads(result)            
            vnf_name = {"vnf_id":filename[:-4]}            
            json_result['schema'] = vnf_name
            json_result['vnf'] = json_result.pop('schema')
            json_result['correlations'] = json_result.pop('data')                      
            mongo_db.insert_docs(db_name, dict_coll, json_result)        
    logger.info("Training Finished succesfully")
    response = {'response':'Training was successful. Correlation dictionaries were updated'}      
    return Response(json.dumps(response),  mimetype='application/json')
     
@app.route('/tng-sdk-analyze-weight/api/weight/v1/<ns_uuid>', methods=['GET'])
def correlation(ns_uuid):
    logger.warning("Logging get weights for a NS")
    dictionaries = list()
    unknown_vnfs_list = list()
    http_code = meth.get_http_code(ns_uuid)
    if http_code == 200:
        logger.info("Call to the Catalogue", extra={"http_code": http_code})
        nsd = meth.get_ns(ns_uuid)
        vnfs = meth.extract_vnfs(nsd)
        logger.info("Extract VNFs from the NS")
        dictionaries = mongo_db.get_documents(db_name, dict_coll, vnfs)
        known_vnfs = mongo_db.get_known_vnfs(db_name, dict_coll, vnfs)
        if len(dictionaries) == 0:
            response = "{'response':'The provided VNFs are currently unknown. Try again later'}"   
            mongo_db.add_to_unknown(db_name, unk_vnf_coll, vnfs)
            logger.info("Unknown VNFs added to collection")            
            return Response(json.dumps(response),  mimetype='application/json')
        if len(dictionaries) > 0 and len(dictionaries) < len(vnfs):
            for vnf in vnfs:
                if vnf not in known_vnfs:
                    unknown_vnfs_list.append(vnf)
            mongo_db.add_to_unknown(db_name, unk_vnf_coll, unknown_vnfs_list) 
        logger.info("Return weigth for provided NS")                                    
        return Response(json_enc().encode(dictionaries),  mimetype='application/json')        
    else:
        logger.error("error", extra={"http_code": http_code})
    return ""
         
@app.route('/tng-sdk-analyze-weight/api/weight/v1/train/new/vnf/<vnf_type>', methods=['GET','POST'])
def consume_train_data(vnf_type):
    logger.warning("Logging upload dataset for train a VNF")
    file = request.files['file']
    file_name = file.filename
    file_validity = meth.file_validator(file_name)
    file_exist = meth.get_file(file_name)
    if (file_validity == True and file_exist == False and mongo_db.not_in_db(db_name, dict_coll, vnf_type) == True):
        file.save(os.path.join(UPLOAD_DADA_FOLDER, file_name))
        logger.info("File validated and uploaded")
        meth.train_vnf(vnf_type, file_name)
        logger.info("Training for provided VNF started")
        response = "{'response':'File was successfully uploaded. Train started '}"
        return Response(json.dumps(response),  mimetype='application/json')
    if (file_validity == False ):
        response = "{'response':'There was an error with the file.','error': 'File not .csv'}"  
        return Response(json.dumps(response),  mimetype='application/json')  
    if (file_exist == True ):
        response = "{'response':'There was an error with the file.','error': 'File already exists'}"  
        return Response(json.dumps(response),  mimetype='application/json')  
    if (mongo_db.not_in_db(db_name, dict_coll, vnf_type) == False ):
        response = "{'response':'There was an error with the vnf type.','error': 'Vnf type already exists'}"  
        return Response(json.dumps(response),  mimetype='application/json')
    logger.error("")
    return 

@app.route('/tng-sdk-analyze-weight/api/weight/v1/vnftype', methods=['GET'])
def correlated_vnf():
    logger.warning("Logging get weights for a VNF type")
    unknown_vnfs_list = list()
    logger.info("Retrieve unknown VNFs")
    provided_vnfs = request.args.get('vnf_type')
    vnfs_list = provided_vnfs.split(',')
    dictionaries = mongo_db.get_documents(db_name, dict_coll,vnfs_list)
    known_vnfs = mongo_db.get_known_vnfs(db_name, dict_coll,vnfs_list)
    if len(dictionaries) == 0:
        response = "{'response':'The provided VNFs are currently unknown. Try again later'}"   
        mongo_db.add_to_unknown(db_name, unk_vnf_coll, vnfs_list)            
        return Response(json.dumps(response),  mimetype='application/json')
    if len(dictionaries) > 0 and len(dictionaries) < len(vnfs_list):        
        for vnf in vnfs_list:
            if vnf not in known_vnfs:
                unknown_vnfs_list.append(vnf)
        mongo_db.add_to_unknown(db_name, unk_vnf_coll, unknown_vnfs_list)
    logger.info("Weights for provided VNFs retrieved")
    return Response(json_enc().encode(dictionaries),  mimetype='application/json')

@app.route('/tng-sdk-analyze-weight/api/weight/v1/mgmt/knownvnfs', methods=['GET'])
def vnf_dictionaries():
    logger.warning("Logging get supported VNF types")
    response = mongo_db.get_supported_vnfs(db_name, dict_coll)
    logger.info("Supported VNFs retrieved")
    return Response(json.dumps(response),  mimetype='application/json')  
 
app.run(host='0.0.0.0', port=8084, debug=True)