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
import requests
import os
import json
import database.db_connect as mongo_db

UPLOAD_DADA_FOLDER = 'data'
ALLOWED_EXTENSIONS = set(['csv'])


def get_redundant_pairs(df):
    '''Get diagonal and lower triangular pairs of correlation matrix'''
    pairs_to_drop = set()
    cols = df.columns
    for i in range(0, df.shape[1]):
        for j in range(0, i+1):
            pairs_to_drop.add((cols[i], cols[j]))
    return pairs_to_drop

def get_top_abs_correlations(df, n):
    '''Sort and return top n Correlated pairs'''
    au_corr = df.corr().abs().unstack()
    labels_to_drop = get_redundant_pairs(df)
    au_corr = au_corr.drop(labels=labels_to_drop).sort_values(ascending=False)
    json_result = au_corr[0:n].to_json(orient='table')
    return json_result

def get_http_code(ns_uuid):
    url = 'http://pre-int-sp-ath.5gtango.eu:4011/catalogues/api/v2/network-services/' + ns_uuid
    headers = {'Content-type': 'application/json'}
    try:
        response = requests.get(url, headers=headers)
        return response.status_code
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        return e
    
def get_ns(ns_uuid):
    url = 'http://pre-int-sp-ath.5gtango.eu:4011/catalogues/api/v2/network-services/' + ns_uuid
    headers = {'Content-type': 'application/json'}
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        return e
    
def extract_vnfs(nsd):
    vnfs = nsd["nsd"]["network_functions"]
    vnfs_id = list()
    for vnf in vnfs:
        vnfs_id.append(vnf["vnf_id"])
    return vnfs_id

def train_vnf(vnf_type, file_name):     
    d = pd.read_csv(UPLOAD_DADA_FOLDER+"\\"+file_name, index_col=0)
    df = pd.DataFrame(data = d)
    result = get_top_abs_correlations(df, 5) 
    json_result = json.loads(result)            
    vnf_name = {"vnf_id":vnf_type}            
    json_result['schema'] = vnf_name
    json_result['vnf'] = json_result.pop('schema')
    json_result['correlations'] = json_result.pop('data')                      
    mongo_db.insert_docs("tng-sdk-analysis-weight", "dictionaries", json_result)
    return ""

def tsplit(string, delimiters):
    delimiters = tuple(delimiters)
    stack = [string,]
    
    for delimiter in delimiters:
        for i, substring in enumerate(stack):
            substack = substring.split(delimiter)
            stack.pop(i)
            for j, _substring in enumerate(substack):
                stack.insert(i+j, _substring)           
    return stack

def file_validator(file_name):
    file_type = file_name[-3:]
    if file_type == "csv":
        return True
    else:
        return False 

def get_file(file_name):
    exists = os.path.isfile(os.path.join(UPLOAD_DADA_FOLDER,file_name))
    return exists
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS