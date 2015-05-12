# -*- coding: utf-8 -*-
import re


class Article:

    def __init__(self, data, source):  # TODO: add use of MissingParameterError
        if source == 'IEEE':
            self._init_from_ieee_xml(data)
        elif source == 'Springer':
            self._init_from_springer_json(data)

    def _init_from_ieee_xml(self, data):
        abstract_text_raw = data.find('abstract').text
        self.abstract_text = self._remove_html_tags(abstract_text_raw)
        self.publication_year = data.find('py').text
        self.doi = data.find('doi').text
        self.title = data.find('title').text

    def _init_from_springer_json(self, data):
        abstract_text_raw = data.get('abstract')
        abstract_text = self._remove_html_tags(abstract_text_raw)
        abstract_text = abstract_text.strip()
        if abstract_text.startswith('Abstract'):
            abstract_text = abstract_text[8:]  # removing Abstract word
        if abstract_text.startswith('Background'):
            abstract_text = abstract_text[10:]
        if abstract_text.startswith('Introduction'):
            abstract_text = abstract_text[12:]
        self.abstract_text = abstract_text

        pub_date = data.get('publicationDate')
        if pub_date is not None:
            self.publication_year = pub_date.split('-')[0]

        self.doi = data.get('doi')
        self.title = data.get('title')

    @staticmethod
    def _remove_html_tags(text, unsafe=True):

        def extract_value(match_obj):
            return match_obj.group('value')

        tag_pattern = '<(?P<tag>\w+)>(?P<value>.*?)</(?P=tag)>'
        result = re.sub(tag_pattern, extract_value, text)
        if unsafe:
            result = re.sub('<[^>]*>', '', result)

        return result
