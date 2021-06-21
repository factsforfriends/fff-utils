#!/usr/bin/env python

import os
import sys
import json
from slugify import slugify

from .trello import connect_board, get_custom_field_value, extract_source_url
from .unsplash import retrieve_url, get_binary_photo
from .aws import upload_object
from .strapi import push

def trello_strapi(args, log):
    '''
    Manages the data upload from a Trello board to the Strapi CMS.
    '''
    # Get list to operate on
    board = connect_board(args.board, log)
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
        log.debug('Found custom fields {} on card {}'.format(','.join(custom_fields.keys()), title))

        # Extract custom fields
        id = get_custom_field_value('id', custom_fields, '', log=log)
        date = get_custom_field_value('datum', custom_fields, '?', log=log)
        category = get_custom_field_value('kategorie', custom_fields, 'None', log=log)
        medium = get_custom_field_value('medium', custom_fields, '', log=log)
        image = get_custom_field_value('bild', custom_fields, '', log=log)

        # Get unsplash image 
        if image != '':
            image_source_url = retrieve_url(image, 'regular', log=log)
            
            # Upload image to AWS
            upload_object(get_binary_photo(image_source_url), image+'.jpg', 'fff-snack-images', log=log)

            image_url = 'https://fff-snack-images.s3.amazonaws.com/'+image+'.jpg'
            log.debug('Uploaded image {} from Unsplash to AWS'.format(image))
        else:
            image_url = ''
        
        d = {
            "_id": id,
            "slug": slugify(title),
            "headline": title,
            "snack": text,
            "url": source,
            "date": date,
            "category": category,
            "medium": medium,
            "image_url": image_url
        }

        #
        # Logic to push snack to Strapi
        #
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

def local_strapi(args, log):
    '''
    Uploads data from a local JSON file to Strapi
    '''
    with open(args.data, 'r') as json_file:
        data = json.load(json_file)
        responses = push(data, log)

    return(responses)