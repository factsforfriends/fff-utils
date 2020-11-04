#!/usr/bin/env python

import argparse
import logging
from .fetch_trello import fetch_trello

def main():
    parser = argparse.ArgumentParser(description='Utilities for FactsForFriends')
    parser.add_argument('--debug', action='store_true', help='Print verbose messages (for debugging)')
    subparsers = parser.add_subparsers()
    
    # Command-line arguments for the fetch command
    parser_fetch = subparsers.add_parser('fetch', help='Fetch latest snacks from a Trello board.')
    parser_fetch.add_argument('--board', help='ID of the Trello board', type=str, required=True)
    parser_fetch.add_argument('--from-list', help='ID of the list containing incoming snacks', type=str, required=True)
    parser_fetch.add_argument('--move-to', help='ID of the list where processed snacks should be moved to', type=str, required=False)
    parser_fetch.set_defaults(func=fetch_trello)

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
    res = args.func(args, logger)
    print(res)