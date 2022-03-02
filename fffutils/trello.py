#!/usr/bin/env python

import os
import sys
import json
from trello import TrelloClient

def connect_board(id, log=None):
    '''
    Connects to a Trello board with ID id
    '''
    # Get neccessary environmental variables
    trello_api_key = os.getenv('TRELLO_API_KEY', '')
    trello_api_secret = os.getenv('TRELLO_API_SECRET', '')

    if trello_api_key == '' or trello_api_secret == '':
        if log is not None:
            log.error('Could not find Trello API credentials in environment. Please set TRELLO_API_KEY and TRELLO_API_SECRET.')
        sys.exit(1)

    # Create connection to Trello
    client = TrelloClient(api_key = trello_api_key, api_secret = trello_api_secret)

    return(client.get_board(id))

def get_custom_field_value(name, fields, default='', log=None):
    '''
    Helper function to obtain the value of a custom field
    '''
    try:
        val = fields[name]
    except:
        if log is not None:
            log.debug('Could not get custom field {}'.format(name))
        return(default)
    return(val.rstrip())

def extract_attachments(card):
    '''
    Helper function to extract URLs and images from a cards attachments
    '''
    attachments = list()
    for attachment in card.attachments:
        attachment_type = ''
        if attachment['url'].startswith('http'):
            if attachment['name'].endswith('.png'):
                attachment_type = 'sharepic'
            else:
                attachment_type = 'source'
        
        if attachment_type is not '':
            attachments.append({'type': attachment_type, 'url': attachment['url']})
    
    return(attachments)
