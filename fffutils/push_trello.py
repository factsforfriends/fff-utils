#!/usr/bin/env python

import os
import sys
import json
from trello import TrelloClient

def push_trello(args, log):
    # Get neccessary environmental variables
    trello_api_key = os.getenv('TRELLO_API_KEY', '')
    trello_api_secret = os.getenv('TRELLO_API_SECRET', '')

    if trello_api_key == '' or trello_api_secret == '':
        sys.exit('Could not find Trello API credentials in environment. Please set TRELLO_API_KEY and TRELLO_API_SECRET.')

    # Create connection to Trello
    client = TrelloClient(api_key = trello_api_key, api_secret = trello_api_secret)
    
    # Get list to operate on
    board = client.get_board(args.board)
    output_list = board.get_list(args.to_list)

    # Fetch custom field definitions
    custom_fields_definition = board.get_custom_field_definitions()
    custom_fields = dict(zip([x.name.lower() for x in custom_fields_definition], custom_fields_definition))

    # Add missing custom fields to board

    with open(args.data, 'r') as json_file:
        data = json.load(json_file)
        for snack in data:
            # Create the card
            card = output_list.add_card(
                name = snack['headline'],
                desc = snack['snack'],
                position = "top"
            )

            # Add URL attachment
            card.attach(name = 'Source', url = snack['url'])

            # If possible, add custom fields
            try:
                card.set_custom_field(snack['createdAt'], custom_fields['datum'])
            except:
                log.debug('Could not set custom field \'Datum\' for card {}'.format(card.name))
                pass
            
            try:
                card.set_custom_field(snack['category'], custom_fields['kategorie']) 
            except:
                log.debug('Could not set custom field \'Kategorie\' for card {}'.format(card.name))
                pass

            try:
                card.set_custom_field(snack['medium'], custom_fields['medium'])
            except:
                log.debug('Could not set custom field \'Medium\' for card {}'.format(card.name))
                pass

            try:
                card.set_custom_field(snack['tags'], custom_fields['tags']) 
            except:
                log.debug('Could not set custom field \'Tags\' for card {}'.format(card.name))
                pass

            log.debug('Added card {name} to list {list} on board {board}'.format(name = card.name, list = output_list.name, board = board.name))

