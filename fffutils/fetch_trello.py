#!/usr/bin/env python

import os
import sys
import json
from trello import TrelloClient
from slugify import slugify
import spacy

from .push_cms import push
from .image import recommend_images, load_keywords, load_keyword_matcher

def connect_board(id, log=None):
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
    try:
        val = fields[name]
    except:
        if log is not None:
            log.error('Could not get custom field {}'.format(name))
        return(default)
    return(val.rstrip())

def fetch_trello(args, log):
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
        
        d = {
            "_id": id,
            "slug": slugify(title),
            "headline": title,
            "snack": text,
            "url": source,
            "date": date,
            "category": category,
            "medium": medium,
            "image_url": image
        }

        #
        # Login to recommend images for the card, if no image is chosen
        #
        if args.recommend_images and image == '':
            nlp = spacy.load("de_core_news_md")

            prediction_categories = ["gesundheit", "politik"]
            if category.lower() in prediction_categories:
                keywords = load_keywords(prediction_categories, nlp, log=log)
                matcher = load_keyword_matcher(keywords, nlp, log=log)

                # Predict image based on headline and first sentence
                recommender_text = d["headline"] + d["snack"].split(".")[0]
                image_ids = recommend_images(recommender_text, matcher[category.lower()], nlp, 3)

                if len(image_ids) > 0:
                    # Get image name, instead of its id
                    image_names = [keywords[category.lower()][int(id)]['name'] for id in image_ids]

                    # Comment recommendations on card
                    image_texts = ['Use `{}` for https://unsplash.com/photos/{}'.format(name, name) for name in image_names]
                    card.comment('**Image recommendations**\n' + '\n'.join(image_texts))
                else:
                    card.comment('I could not find a suitable image :-(')
            else:
                log.debug('Category {} missing for image recommendation'.format(category.lower()))

        #
        # Logic to push snack to the CMS
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

def extract_source_url(card):
    source = ''

    for attachment in card.attachments:
        if attachment['url'].startswith('http'):
            source = attachment['url']
    
    if source == '':
        raise Exception('No valid source URL found in attachments.')
    return(source)
