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

import json
import os
import logging
import pymongo
from pymongo import MongoClient


cat_url = os.environ['CATALOGUES_URL']
db_host = os.environ['DATABASE_HOST']
db_port = os.environ['DATABASE_PORT']
db_name = os.environ['DATABASE_NAME']
dict_coll = os.environ['DICT_COLL']
unk_vnf_coll = os.environ['UNK_COLL']
enc_fig_coll = os.environ['ENC_FIGS_COLL']
log_level = os.environ['LOG_LEVEL']

# cat_url  = "http://tng-cat:4011/catalogues/api/v2/"
# db_host = "mongo"
# db_port = 27017
# db_name = "tng-sdk-analyze-weight"
# dict_coll = "dictionaries"
# unk_vnf_coll = "unknown_vnfs"
# enc_fig_coll = "encoded_figs"
# log_level = "INFO"

logger = logging.getLogger()

def mongo_connect():
    logger.info("Logging Connection to Mongo")
    client = MongoClient()
    try:
        client = MongoClient(db_host, 27017)       
    except pymongo.errors.PyMongoError as e:
        logger.error("Could not connect to database:",  extra={"error": e})
    return client

def create_db(db_name):
    logger.info("Logging Create Db")
    client = mongo_connect()
    my_db = client[db_name]
    client.close()

def insert_docs(db, collection, doc):
    logger.info("Logging Insert Doc to Mongo " + str(doc))
    client = mongo_connect()
    db = client[db]
    collection_doc = db[collection]
    
    #collection_doc.insert(doc)
    collection_doc.update(doc, doc, upsert = True)
    client.close()

def add_to_unknown(db, collection, vnfs):
    logger.info("Logging Insert unknown vnf to Mongo " + str(vnfs))
    client = mongo_connect()
    db = client[db]
    collection = db[collection]
    
    for vnf in vnfs:
        #collection.insert_one({'vnf_id': vnf})
        collection.update({'vnf_id': vnf}, {'vnf_id': vnf}, upsert = True)
    client.close()

def add_fig_to_db(db, collection, encoded_fig, vnf_type):
    logger.info("Logging base64 fig to Mongo " + str(vnf_type))
    client = mongo_connect()
    db = client[db]
    collection = db[collection]
    collection.insert_one({'vnf_id': vnf_type,
                            'encoded_fig': encoded_fig})
    client.close()
      
def del_doc(db, collection, doc):
    logger.info("Logging delete Doc from Mongo" + str(doc))
    client = mongo_connect()
    mydb = client[db]
    mycol = mydb[collection]

    with open(doc) as f:
        file_data = json.load(f)

    mycol.delete_one(file_data)
    client.close()
    

def get_documents(db, collection,vnf_names):
    logger.info("Logging retrieve Docs to Mongo " + str(vnf_names))
    documents_list = list()
    client = mongo_connect()

    mydb = client[db]
    mycol = mydb[collection]
       
    for vnf_name in vnf_names:
        myquery = { 'vnf': {
                    'vnf_id':vnf_name
                    } 
                  }
        cursor = mycol.find(myquery)
  
        for document in cursor:
            documents_list.append(document)
                     
    client.close()
    return documents_list

def get_fig_base64(db, collection, vnf_type):  
    logger.info("Logging get fig base64 from Mongo" + str(vnf_type))  
    client = mongo_connect()

    mydb = client[db]
    mycol = mydb[collection]
       
    myquery = {'vnf_id': vnf_type}
    cursor = mycol.find(myquery)
    for document in cursor:        
        html = "<img src=\"data:image/png;base64,"+document['encoded_fig'].decode('utf-8')+"\"\>"                         
    client.close()
    return html

def get_known_vnfs(db, collection,vnf_names):
    logger.info("Logging get known vnfs from Mongo " + str(vnf_names))
    client = mongo_connect()
    known_vnfs = list()
    mydb = client[db]
    mycol = mydb[collection]
       
    for vnf_name in vnf_names:
        myquery = { 'vnf': {
                    'vnf_id':vnf_name
                    } 
                  }
        cursor = mycol.count(myquery)
        if cursor > 0:
            known_vnfs.append(vnf_name)
                              
    client.close()
    return known_vnfs

def not_in_db(db, collection, vnf):
    logger.info("Logging check if vnf exists in db " + vnf)
    client = mongo_connect()
    mydb = client[db]
    mycol = mydb[collection]
    
    myquery = { 'vnf': {
                    'vnf_id':vnf
                    } 
                  }
    cursor = mycol.count(myquery)
    
    if cursor == 0:
        return True
    else:
        return False
    
    
def get_supported_vnfs(db, collection):
    logger.info("Logging get supported VNFS from " + str(collection))
    documents_list = list()
    vnfs_list = list()
    client = mongo_connect()
    mydb = client[db]
    mycol = mydb[collection]
       
    cursor = mycol.find({})
    for document in cursor:
        documents_list.append(document)
    
    for field in documents_list:
        vnfs_list.append(field['vnf']['vnf_id'])   
    client.close()    
    return vnfs_list

def get_unsupported_vnfs(db, collection):
    logger.info("Logging get unsupported VNFS from" + str(collection))
    documents_list = list()
    vnfs_list = list()
    client = mongo_connect()
    mydb = client[db]
    mycol = mydb[collection]
       
    cursor = mycol.find({})
    for document in cursor:
        documents_list.append(document)
        
    for field in documents_list:
        vnfs_list.append(field['vnf_id'])   
    client.close()    
    return vnfs_list

def drop_collection(db, collection):
    logger.info("Logging drob collection" + str(collection))
    client = mongo_connect()
    mydb = client[db]
    collection_doc = mydb[collection].drop()
    client.close()