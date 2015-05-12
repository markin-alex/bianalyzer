# -*- coding: utf-8 -*-
from bisect import bisect_left
import re
import nltk
from nltk.stem.porter import PorterStemmer

from .stop_words import sorted_stop_words

porter_stemmer = PorterStemmer()


class BianalyzerText:

    def __init__(self, text, tag_pos=False, strip_stop_words=True, use_pos_filter=False, pos_list=('NN', 'NNP', 'NNS')):
        self.text = text
        self.pos_list = pos_list
        self.tagged_tokens = None
        self.word_list = self._tokenize_text(tag_pos, strip_stop_words, use_pos_filter)
        self.text_length = len(self.word_list)
        self.word_dict = {}
        self.stemmed_word_dict = {}
        self._construct_word_dictionaries()

    def tag_tokens(self):
        self.tagged_tokens = nltk.pos_tag(self.all_tokens)
        return self.tagged_tokens

    def _tokenize_text(self, tag_pos=False, strip_stop_words=True, use_pos_filter=False):
        tokens = nltk.word_tokenize(self.text.lower())
        self.all_tokens = tokens
        if tag_pos:
            self.tagged_tokens = nltk.pos_tag(tokens)
        words = self._filter_tokens(tokens, use_pos_filter, strip_stop_words)

        return words

    def _construct_word_dictionaries(self):
        for (position, word) in enumerate(self.word_list):
            word_occurrences = self.word_dict.get(word, [])
            word_occurrences.append(position)
            self.word_dict[word] = word_occurrences

            stemmed_word = porter_stemmer.stem(word)
            stemmed_word_occurrences = self.stemmed_word_dict.get(stemmed_word, [])
            stemmed_word_occurrences.append(position)
            self.stemmed_word_dict[stemmed_word] = stemmed_word_occurrences

    def _filter_tokens(self, tokens, filter_stop_words, use_pos_filter):
        filtered_words = []
        for word in tokens:
            word_fits = re.match('^[a-zA-Z\'-]{2,}$', word) is not None
            if use_pos_filter:
                word, pos = nltk.pos_tag([word])[0]
                word_fits = word_fits and (pos in self.pos_list)
            if filter_stop_words:
                ind = bisect_left(sorted_stop_words, word)
                word_fits = word_fits and (ind >= len(sorted_stop_words) or sorted_stop_words[ind] != word)

            if word_fits:
                filtered_words.append(word)

        return filtered_words
