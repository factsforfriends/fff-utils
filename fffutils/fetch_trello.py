#!/usr/bin/env python

import os
import sys
import json
from trello import TrelloClient
from slugify import slugify

from .push_cms import push

def fetch_trello(args, log):
    # Get neccessary environmental variables
    trello_api_key = os.getenv('TRELLO_API_KEY', '')
    trello_api_secret = os.getenv('TRELLO_API_SECRET', '')

    if trello_api_key == '' or trello_api_secret == '':
        sys.exit('Could not find Trello API credentials in environment. Please set TRELLO_API_KEY and TRELLO_API_SECRET.')

    # Create connection to Trello
    client = TrelloClient(api_key = trello_api_key, api_secret = trello_api_secret)
    
    # Get list to operate on
    board = client.get_board(args.board)
    input_list = board.get_list(args.from_list)

    # Fetch custom field definitions
    custom_fields_definition = board.get_custom_field_definitions()
    custom_fields_definition_list = dict(zip([x.name.lower() for x in custom_fields_definition], custom_fields_definition))

    results = list()
    for card in input_list.list_cards():
        title = card.name
        text = card.description
        
        try:
            source = extract_source_url(card)
        except Exception as e:
            # Add label to card to indicate missing source URL
            log.error(e)
            next
        
        # Extract custom fields
        custom_fields = dict(zip([x.name.lower() for x in card.custom_fields], [x.value for x in card.custom_fields]))
        log.debug('Found custom fields: {}'.format(",".join(custom_fields.keys())))

        # Extract CMS ID
        try:
            id = custom_fields['id']
        except:
            id = ''
            pass

        # Extract date
        try:
            date = custom_fields['datum']
        except:
            date = '?'
            card.create_label('Date missing', 'red')
            log.debug('Could not get custom field \'Datum\' for card {}'.format(card.name))
            pass

        # Extract category
        try:
            category = custom_fields['kategorie']
        except:
            # predict category
            category = 'None'
            log.debug('Could not get custom field \'Kategorie\' for card {}'.format(card.name))
            pass
        
        # Extract medium
        try:
            medium = custom_fields['medium']
        except:
            # predict medium
            medium = 'None'
            log.debug('Could not get custom field \'Medium\' for card {}'.format(card.name))
            pass
        # Predict medium, location, category, tags
        
        d = {
            "_id": id,
            "slug": slugify(title),
            "headline": title,
            "snack": text,
            "url": source,
            "date": date,
            "category": category,
            "medium": medium
        }

        # Push to CMS?
        if args.push:
            res = push(d, log)[0]

            try:
                response = json.loads(res.data)
            except:
                log.error('Received status {} with message: {}'.format(res['statusCode'], res['message']))

            # Update ID from CMS
            try:
                card.set_custom_field(response['_id'], custom_fields_definition_list['id'])
            except:
                log.error('Could not to set card ID to {}'.format(response['_id']))
        
            if args.move_to != '' and res.status == 200:
                # Remove labels?
                card.change_list(args.move_to)
        
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
