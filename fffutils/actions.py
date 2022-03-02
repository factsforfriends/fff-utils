#!/usr/bin/env python

import os
import sys
import json
import datetime
import dateutil.parser
import spacy
from slugify import slugify

from .trello import connect_board, get_custom_field_value, extract_attachments
from .unsplash import retrieve_url, get_binary_photo
from .aws import upload_object
from .strapi import push, get_facts, add_recommendation, add_collection
from .helper import split_claim_fact, stopwords
from .nlp import find_similar_docs

def trello_collections(args, log):
    '''
    Manages the upload of collections from a Trello board to the Strapi CMS.
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
        comment = card.description

        # Extract custom fields
        custom_fields = dict(zip([x.name.lower() for x in card.custom_fields], [x.value for x in card.custom_fields]))
        log.debug('Found custom fields {} on card {}'.format(','.join(custom_fields.keys()), title))

        id = get_custom_field_value('id', custom_fields, '', log=log)
        date = get_custom_field_value('datum', custom_fields, str(datetime.datetime.now().replace(microsecond=0).isoformat()), log=log)

        # Handle attachments
        attachments = [a for a in extract_attachments(card) if a['type'] == 'source']

        # Consolidate urls to id only
        facts = [os.path.split(a['url'])[1] for a in attachments]

        res = add_collection(title, comment, date, facts, id, log)
        response = json.loads(res.data)
        
        # Update ID from CMS
        try:
            print(response)
            card.set_custom_field(response['_id'], custom_fields_definition_list['id'])
        except:
            log.error('Could not to set card ID to {}'.format(response['_id']))
        results.append(response)

    return(results)

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
        (claim, fact) = split_claim_fact(card.description)
        slug = slugify(title, stopwords = stopwords())
        
        # Handle attachments to find URL and Sharepic
        attachments = extract_attachments(card)

        try:
            source = [a for a in attachments if a['type'] == 'source'][0]['url']
        except KeyError:
            log.error('Missing source URL on snack {}'.format(title))
            break
        
        sharepic_source_urls = [a for a in attachments if a['type'] == 'sharepic']

        if len(sharepic_source_urls) > 0:
            sharepic_source_url = sharepic_source_urls[0]['url']

            # Construct auth header
            trello_api_key = os.getenv('TRELLO_API_KEY', '')
            trello_api_secret = os.getenv('TRELLO_API_SECRET', '')
            headers = {'Authorization': 'OAuth oauth_consumer_key="{}", oauth_token="{}"'.format(trello_api_key, trello_api_secret)}
            
            # Upload image to AWS
            upload_object(get_binary_photo(sharepic_source_url, headers=headers, log=log), slug+'.png', 'fff-sharepics', content_type = 'image/png', log=log)
            sharepic_url = 'https://fff-sharepics.s3.amazonaws.com/'+slug+'.png'
        else: 
            sharepic_url = ''
            log.debug('Missing sharepic URL on snack {}'.format(title))
        
        # Extract custom fields
        custom_fields = dict(zip([x.name.lower() for x in card.custom_fields], [x.value for x in card.custom_fields]))
        log.debug('Found custom fields {} on card {}'.format(','.join(custom_fields.keys()), title))

        id = get_custom_field_value('id', custom_fields, '', log=log)
        date = get_custom_field_value('datum', custom_fields, str(datetime.datetime.now().replace(microsecond=0).isoformat()), log=log)
        category = get_custom_field_value('kategorie', custom_fields, 'None', log=log)
        medium = get_custom_field_value('medium', custom_fields, '', log=log)
        tags = get_custom_field_value('tags', custom_fields, '', log=log)
        image = get_custom_field_value('bild', custom_fields, '', log=log)

        # Get unsplash image 
        if image != '':
            image_source_url = retrieve_url(image, 'regular', log=log)
            
            # Upload image to AWS
            upload_object(get_binary_photo(image_source_url, log=log), image+'.jpg', 'fff-snack-images', log=log)

            image_url = 'https://fff-snack-images.s3.amazonaws.com/'+image+'.jpg'
            #log.debug('Uploaded image {} from Unsplash to AWS'.format(image))
        else:
            image_url = ''
        
        d = {
            "_id": id,
            "slug": slug,
            "headline": title,
            "claim": claim,
            "snack": fact,
            "url": source,
            "date": date,
            "category": category,
            "medium": medium,
            "tags": tags,
            "image_url": image_url,
            "sharepic_url": sharepic_url
        }
        log.debug('Final snack looks like {}'.format(d))

        #
        # Logic to push snack to Strapi if date is not newer
        #
        snack_date = dateutil.parser.parse(date)
        if args.push and snack_date.date() <= datetime.date.today():
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

def strapi_recommendations(args, log):
    '''
    Renew fact recommendations on Strapi
    '''
    facts = get_facts(limit = -1, log = log)

    # Get all headline + first sentence from all facts
    raw_recommender_text = [d["headline"] + d["snack"].split(".")[0] for d in facts]

    # load model
    nlp = spacy.load('de_core_news_sm')

    # Consolidate recommender text
    recommender_text = [nlp(" ".join([word.lower() for word in text.replace("Falsch:", "").replace("Fakt:", "").replace("-", " ").split(" ")])) for text in raw_recommender_text]

    # transform texts to documents, use only nouns and propositions
    docs = [nlp(' '.join(str(t) for t in doc if t.pos_ in ['NOUN', 'PROPN', 'ADJ'])) for doc in recommender_text]

    responses = list()
    for doc in docs:
        if log is not None:
            log.debug('Adding {} recommendations for {}'.format(args.n, doc))
            
        idx = find_similar_docs(doc, docs, n = args.n + 1, log = log)

        # Push ids to strapi recommendation table
        fact = facts[idx[args.n]]['id']
        recommendations = [facts[index] for index in idx[:-1]]

        responses.append(add_recommendation(fact, recommendations, log = log))

