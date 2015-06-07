# -*- coding: utf-8 -*-
import traceback
import urllib2
from urllib import urlencode
from datetime import datetime
import lxml
from lxml.etree import XMLSyntaxError
import re

from .article import Article
from ..errors import InvalidArgumentError
from ..helpers import remove_html_tags, construct_similarity_matrix_via_profiles
from ..relevance import RelevanceMatrix, SimilarityMatrix


def download_ieee_abstracts(raw_query, number, start_index=1):
    # constructing query
    query = '(%s)' % raw_query  # enclosed 'raw_query' in brackets
    params = {'querytext': query, 'ctype': 'Journals', 'hc': number, 'rs': start_index}
    query_string = urlencode(params)

    return query_ieee(query_string)


class DLTermType:
    controlled = 0
    thesaurus = 1
    author = 2
    ieee = 3


class IEEEKeywordDownloader:
    def __init__(self, articles, term_type, debug=False):
        if len(articles) <= 0:
            raise InvalidArgumentError('articles', articles, 'The list could not be empty')
        for article in articles:
            if not isinstance(article, Article):
                raise InvalidArgumentError('articles', articles,
                                           'The list should contain only bianalyzer.abstracts.article.Article class instances')
        self.articles = articles
        self.debug = debug  # TODO: consider debug mode
        self._successful_articles = []
        self.term_type = term_type
        self._downloaded = False
        self._keyword_articles = {}

    def download_ieee_keywords(self):
        if self._downloaded:
            return self._keyword_articles.keys()

        term_type = self.term_type
        keyword_articles = {}
        successful_articles = []

        i = 0
        for line, article in enumerate(self.articles):
            doi = article.doi
            keywords = None
            try:
                if term_type in (DLTermType.controlled, DLTermType.thesaurus):
                    keywords = retrieve_ieee_inspec_keywords(doi, term_type)
                elif term_type in (DLTermType.author, DLTermType.ieee):
                    keywords = retrieve_ieee_web_keywords(doi, term_type)
            except Exception, e:
                print 'Error occurred: %s' % e

            if keywords is not None and len(keywords) > 0:
                successful_articles.append(article)
                for keyword in keywords:
                    k_articles = keyword_articles.get(keyword, [])
                    k_articles.append(i)
                    keyword_articles[keyword] = k_articles
                i += 1

            # print 'Processed article #%s: \"%s\"' % (line + 1, article.title)
            # print '-----------------------------------------'

        self._keyword_articles = keyword_articles
        self._downloaded = True
        self._successful_articles = successful_articles
        return keyword_articles.keys()

    def get_binary_relevance_matrix(self):
        if not self._downloaded:
            self.download_ieee_keywords()
        matrix = []
        keywords = []
        for i, (keyword, article_indices) in enumerate(self._keyword_articles.iteritems()):
            matrix.append([])
            for _ in range(len(self._successful_articles)):
                matrix[i].append(0.0)
            for index in article_indices:
                matrix[i][index] = 1.0
            keywords.append(keyword)
        return RelevanceMatrix(keywords, self._successful_articles, matrix, 1.0)

    def get_similarity_matrix(self):
        if not self._downloaded:
            self.download_ieee_keywords()
        keywords = self._keyword_articles.keys()
        profiles = [set(self._keyword_articles[k]) for k in keywords]
        matrix = construct_similarity_matrix_via_profiles(keywords, profiles)
        return SimilarityMatrix(keywords, matrix)


def retrieve_ieee_inspec_keywords(article_doi, term_type):
    params = {'doi': article_doi, 'ctype': 'Journals', 'hc': 1}
    query_string = urlencode(params)
    documents = query_ieee(query_string)
    if documents is None or len(documents) < 1:
        print 'Error on document with doi = %s' % article_doi
    else:
        document = documents[0]
        keywords = None
        if term_type == DLTermType.controlled:
            keywords = find_keyphrases(document, 'controlledterms')
        elif term_type == DLTermType.thesaurus:
            keywords = find_keyphrases(document, 'thesaurusterms')
        return keywords

    return None


def find_keyphrases(document, title):
    keyphrases = set()
    raw = document.find(title)
    if raw is None:
        return keyphrases

    terms = raw.findall('term')
    for term in terms:
        term = term.text
        term = term.lower()
        term = term.strip()
        if re.match('^[\sa-zA-Z\'-]{2,}$', term) is not None:
            keyphrases.add(term)

    return keyphrases


term_types_headers = {DLTermType.author: 'AUTHOR KEYWORDS', DLTermType.ieee: 'IEEE TERMS'}


def retrieve_ieee_web_keywords(article_doi, term_type):
    query_url = 'http://dx.doi.org/' + article_doi
    request = urllib2.Request(query_url)
    response = urllib2.urlopen(request)
    if response.url.startswith('http://ieeexplore.ieee.org:80/xpl/articleDetails.jsp'):
        keywords_url = response.url.replace('articleDetails', 'abstractKeywords')
        kw_request = urllib2.Request(keywords_url)
        kw_response = urllib2.urlopen(kw_request)
        full_html = kw_response.read()
        kw_header = term_types_headers[term_type]
        match = re.search('<div class=\"section\">\s*<h2>' + kw_header + '</h2>(.*?)</div>', full_html,
                          re.MULTILINE + re.DOTALL)
        keywords = set()
        if match is not None:
            keywords_html = match.groups()[0]
            kw_lines = re.findall('<li>(.*?)</li>', keywords_html)
            for kw_line in kw_lines:
                keyword = remove_html_tags(kw_line).strip().lower()
                new_keywords = [kw.strip() for kw in re.split('[,;.]', keyword)
                                if re.match('^[\sa-zA-Z\'-]{2,}$', kw) is not None]
                keywords.update(new_keywords)
        else:
            print 'No author keywords (doi: %s)' % article_doi
        return keywords
    else:
        print 'Unrecognized url: %s; for doi %s' % (response.url, article_doi)

    return None


def query_ieee(query_string):
    query_url = 'http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?' + query_string
    try:
        request = urllib2.Request(query_url)
        response = urllib2.urlopen(request)
        page = response.read().decode('unicode_escape').encode('utf-8', 'ignore')
        page_lines = page.split('\n')

        parsed = False
        while not parsed:
            try:
                response_xml = lxml.etree.fromstring(page)
                parsed = True
            except XMLSyntaxError, e:
                # failed to build xml. Probably trouble with encoding
                # e.position contains line and column of a symbol, where error occurred
                print e.position
                malformed_line, malformed_column = e.position
                malformed_symbol = page_lines[malformed_line - 1][malformed_column - 1]
                page = page.replace(malformed_symbol, '')  # deleting malformed symbol (in most cases we don't need it)

        documents = response_xml.findall('document')
        return documents

    except Exception:
        # TODO: log it
        print traceback.format_exc()
    return []

if __name__ == '__main__':
    first = datetime.now()
    # for i in range(0, 9):
    download_ieee_abstracts('cluster analysis', 500, 1)
    second = datetime.now()
    print (second-first).total_seconds()
