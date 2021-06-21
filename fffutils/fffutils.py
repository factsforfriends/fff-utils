#!/usr/bin/env python

import argparse
import logging
import json
import sys
from .actions import trello_strapi, local_strapi

def main():
    parser = argparse.ArgumentParser(description='Utilities for FactsForFriends')
    parser.add_argument('--debug', action='store_true', help='Print verbose messages (for debugging)')
    subparsers = parser.add_subparsers()
    
    # Command-line arguments for the trello-strapi command
    parser_fetch = subparsers.add_parser('trello-strapi', help='Fetch latest snacks from a Trello board and upload to Strapi.')
    parser_fetch.add_argument('--board', help='ID of the Trello board', type=str, required=True)
    parser_fetch.add_argument('--from-list', help='ID of the list containing incoming snacks', type=str, required=True)
    parser_fetch.add_argument('--move-to', help='ID of the list where processed snacks should be moved to', type=str, required=False)
    parser_fetch.add_argument('--push', help='Indicates if the fetched snacks should be pushed to the CMS.', action='store_true')
    # parser_fetch.add_argument('--recommend-images', help='Indicates if the image recommender should be run.', action='store_true')
    parser_fetch.set_defaults(func=trello_strapi)

    # Command-line arguments for the local-trello command
    parser_push = subparsers.add_parser('local-trello', help='Push local snacks to a Trello board.')
    parser_push.add_argument('--board', help='ID of the Trello board', type=str, required=True)
    parser_push.add_argument('--to-list', help='ID of the list containing incoming snacks', type=str, required=True)
    parser_push.add_argument('--data', help='JSON data to push.', type=str, required=True)
    # parser_push.set_defaults(func=push_trello)

    # Command-line arguments for the local-strapi command
    parser_cms = subparsers.add_parser('local-strapi', help='Push local snacks to Strapi.')
    parser_cms.add_argument('--data', help='JSON data to push.', type=str, required=True)
    parser_cms.set_defaults(func=local_strapi)

    args = parser.parse_args()

    # Add command-line logging
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    sh.setLevel(logging.DEBUG)
    logger.addHandler(sh)

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    # Dispatch function call   
    try:
        res = args.func(args, logger)
    except AttributeError:
        parser.print_help(sys.stderr)
        sys.exit(1)