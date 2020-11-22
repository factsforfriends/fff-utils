from collections import Counter
import spacy
from spacy.matcher import PhraseMatcher
from spacy.lang.de.stop_words import STOP_WORDS

def recommend_images(text, matcher, nlp, n):
    
    # Consolidate text into words
    words = [word.lower() for word in text.replace("Falsch:", "").replace("-", " ").split(" ")]

    # Remove stop words
    words = [word for word in words if word not in STOP_WORDS]

    tokens = nlp(" ".join(words))
    matches = matcher(tokens)

    # Dict with votes per pattern
    votes = dict()
    for (id, start, end) in matches:
        name = nlp.vocab.strings[id]
        if name not in votes.keys():
            votes[name] = 0
        votes[name] = votes[name] + 1
     
    # return top n patterns
    vc = Counter(votes)
    return([name for (name, count) in vc.most_common()[:n]])

def load_keywords(categories, nlp, log = None):
    keyword_dict = dict()
    for category in categories:
        # Add category to dict
        if category not in keyword_dict.keys():
            keyword_dict[category] = list()
        
        # Read in keywords
        with open('fffutils/data/{}-keywords.txt'.format(category)) as f:
            for image in f:
                (id, keywords) = image.split("\t")

                pattern = list(nlp.pipe(keywords.rstrip().lower().split(",")))
                d = {
                    'name': id,
                    'keywords': pattern
                }
                keyword_dict[category].append(d) 
    return(keyword_dict)

def load_keyword_matcher(keyword_dict, nlp, log = None):
    category_matcher = dict()
    for (category,images) in keyword_dict.items():
        category_matcher[category] = PhraseMatcher(nlp.vocab, attr="LEMMA")
        for i, image in enumerate(images):
            category_matcher[category].add(str(i), None, *image["keywords"])
    return(category_matcher)