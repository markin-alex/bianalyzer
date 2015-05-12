# -*- coding: utf-8 -*-
from operator import itemgetter
from nltk import PorterStemmer
from nltk.stem import wordnet

from ..helpers import check_text_collection

wordnet_lemmatizer = wordnet.WordNetLemmatizer()
porter_stemmer = PorterStemmer()


def get_word_frequencies(texts):
    words_frequencies = {}
    for (i, text) in enumerate(texts):
        used_words = {}
        for word in text:
            lem_word = wordnet_lemmatizer.lemmatize(word)
            if not used_words.get(lem_word, False):
                used_words[lem_word] = True
                words_frequencies[lem_word] = words_frequencies.get(lem_word, 0.0) + 1.0

    return words_frequencies


def extract_keywords_via_frequency(bianalyzer_texts, min_freq=0.2, max_freq=15.0):
    check_text_collection(bianalyzer_texts)

    collection = []
    for bianalyzer_text in bianalyzer_texts:
        if bianalyzer_text.text_length > 10:
            collection.append(bianalyzer_text)
    texts = [text.word_list for text in collection]

    word_frequencies = get_word_frequencies(texts)
    articles_num = float(len(collection))
    assert articles_num > 0

    keywords = []
    for (word, freq) in word_frequencies.iteritems():
        absolute_freq = (freq / articles_num) * 100
        if min_freq <= absolute_freq <= max_freq:
            keywords.append((word, round(absolute_freq, 2)))

    keywords = sorted(keywords, key=itemgetter(1))
    print keywords
    print 'extracted: %s' % len(keywords)
    return keywords



