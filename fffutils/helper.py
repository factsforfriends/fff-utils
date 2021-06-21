#!/usr/bin/env python

import re

def split_claim_fact(text, delim = '==='):
    '''
    Helper function to split a text into claim and fact (if possible)
    '''
    parts = [x.strip() for x in re.split(delim, text)]
    if len(parts) == 1:
        return(('', parts[0]))
    else:
        return((parts[0], parts[1]))
