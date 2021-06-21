#!/usr/bin/env python

import os
import sys
import urllib3
import json

def push(data, log = None):
    if not isinstance(data, list): 
        data = [data]

    # Get neccessary JWT auth token
    strapi_auth_token = os.getenv('STRAPI_AUTH_TOKEN', '')

    if strapi_auth_token == '':
        sys.exit('Could not find Strapi JWT auth token in environment. Please set STRAPI_AUTH_TOKEN.')
    
    http = urllib3.PoolManager()
    responses = list()

    for d in data:
        method = 'POST'
        url = 'https://cms.factsforfriends.de/facts'
        
        # If the data has an ID, PUT instead of POST
        id = d.pop('_id', None)
        if id is not None and id != '':
            method = 'PUT'
            url = url + '/' + id

        encoded_data = json.dumps(d).encode('utf-8')
        
        log.debug('Sending {} request to {} with body {}'.format(method, url, encoded_data))

        req = http.request(
            method,
            url,
            body=encoded_data,
            headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + strapi_auth_token})
        responses.append(req)
    
    return(responses)
        
    
