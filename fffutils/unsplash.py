#!/usr/bin/env python

import os
import json
import urllib3

def retrieve_url(id, size, log = None):
    '''
    Retrieves the URL for the Photo with given ID and size.
    '''

    # Get neccessary auth token
    unsplash_access_key = os.getenv('UNSPLASH_ACCESS_KEY', '')
    #unsplash_secret_key = os.getenv('UNSPLASH_SECRET_KEY', '')

    http = urllib3.PoolManager()
    try:
        r = http.request('GET', 
            'https://api.unsplash.com/photos/{}?client_id={}'.format(id, unsplash_access_key),
            )
        data = json.loads(r.data.decode('utf-8'))
    except Exception as e:
        if log is not None:
            log.error(e)
        pass
    
    if 'urls' in data:
        if size in data['urls']:
            return(data['urls'][size])
        else:
            if log is not None:
                log.error('URL for image size {} is not present'.format(size))
            return(None)
    return(None)

def get_binary_photo(url, log = None):
    '''
    Retrieves a binary representation of the image at url
    '''
    http = urllib3.PoolManager()
    try:
        r = http.request('GET', url)
        return(r.data)
    except Exception as e:
        if log is not None:
            log.error(e)
        return(None)