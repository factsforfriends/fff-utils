#!/usr/bin/env python

import numpy as np

def find_similar_docs(text, corpus, n = 3, log = None):
    '''
    Take a text (doc) and a corpus of other texts (docs) and return the indices of the n most similar items from corpus
    '''
    similarities = list()

    if log is not None:
        log.debug('Finding similar docs for {}'.format(text))

    for doc in corpus:
        similarities.append(doc.similarity(text))
    
    return(np.array(similarities).argsort()[-n:])


