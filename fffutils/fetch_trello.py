#!/usr/bin/env python

import os
import sys
from trello import TrelloClient
from slugify import slugify

def fetch_trello(args, log):
    # Get neccessary environmental variables
    trello_api_key = os.getenv('TRELLO_API_KEY', '')
    trello_api_secret = os.getenv('TRELLO_API_SECRET', '')

    if trello_api_key == '' or trello_api_secret == '':
        sys.exit('Could not find Trello API credentials in environment. Please set TRELLO_API_KEY and TRELLO_API_SECRET.')

    # Create connection to Trello
    client = TrelloClient(api_key = trello_api_key, api_secret = trello_api_secret)
    
    # Get input list to operate on
    input_list = client.get_board(args.board).get_list(args.from_list)

    results = list()
    for card in input_list.list_cards():
        title = card.description.split('\n')[0]
        text = '\n'.join(card.description.split('\n')[1:])
        
        try:
            source = extract_source_url(card)
        except Exception as e:
            # Add label to card to indicate missing source URL
            log.error(e)
            next
        
        # Extract dates
        # Predict medium, location, category, tags
        
        d = {
            'slug': slugify(title),
            'title': title,
            'text': text,
            'source': source
        }
        results.append(d)

    return(results)

def extract_source_url(card):
    source = ''

    for attachment in card.attachments:
        if attachment['url'].startswith('http'):
            source = attachment['url']
    
    if source == '':
        raise Exception('No valid source URL found in attachments.')
    return(source)