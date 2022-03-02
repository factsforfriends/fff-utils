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

def add_recommendation(fact, recommendations, log = None):
    # Get neccessary JWT auth token
    strapi_auth_token = os.getenv('STRAPI_AUTH_TOKEN', '')

    if strapi_auth_token == '':
        sys.exit('Could not find Strapi JWT auth token in environment. Please set STRAPI_AUTH_TOKEN.')
    
    http = urllib3.PoolManager()
    url = 'https://cms.factsforfriends.de/recommendations'

    body = dict()
    body['fact'] = fact
    body['recommends'] = recommendations
    encoded_data = json.dumps(body).encode('utf-8')

    if log is not None:
        log.debug('Sending POST request to {} with body {}'.format(url, encoded_data))

    req = http.request(
            'POST',
            url,
            body=encoded_data,
            headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + strapi_auth_token})
    
    return(req)

def add_collection(name, comment, valid_through, facts, id = None, log = None):
    # Get neccessary JWT auth token
    strapi_auth_token = os.getenv('STRAPI_AUTH_TOKEN', '')

    if strapi_auth_token == '':
        sys.exit('Could not find Strapi JWT auth token in environment. Please set STRAPI_AUTH_TOKEN.')
    
    http = urllib3.PoolManager()
    url = 'https://cms.factsforfriends.de/collections'

    body = dict()
    body['name'] = name
    body['comment'] = comment
    body['valid_through'] = valid_through
    body['facts'] = facts
    encoded_data = json.dumps(body).encode('utf-8')

    if id is not None and id != '':
        method = 'PUT'
        url = url + '/' + id
    else:
        method = 'POST'

    if log is not None:
        log.debug('Sending {} request to {} with body {}'.format(method, url, encoded_data))

    req = http.request(
            method,
            url,
            body=encoded_data,
            headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + strapi_auth_token})
        
    return(req)


def get_facts(limit = -1, log = None):
    http = urllib3.PoolManager()
    req = http.request('GET', 'https://cms.factsforfriends.de/facts?_limit=' + str(limit))
        
    try:
        return(json.loads(req.data))
    except TypeError as e:
        if log is not None:
            log.warning('A database request returned a non-str response.')
        return(list())
            
