# -*- coding: utf-8 -*-
import traceback
import urllib2
from urllib import urlencode
from datetime import datetime
from enum import Enum
import lxml
from lxml.etree import XMLSyntaxError
import re


class DLKeywordTypes(Enum):
    controlled = 0
    thesaurus = 1
    both = 2


def download_ieee_abstracts(raw_query, number, start_index=1):
    # constructing query
    query = '(%s)' % raw_query  # enclosed 'raw_query' in brackets
    params = {'querytext': query, 'ctype': 'Journals', 'hc': number, 'rs': start_index}
    query_string = urlencode(params)

    return query_ieee(query_string)


def download_ieee_keywords(articles):
    start_time = datetime.now()
    article_keywords = {}
    for i, article in enumerate(articles):
        doi = article.doi
        params = {'doi': doi, 'ctype': 'Journals', 'hc': 1}
        query_string = urlencode(params)
        documents = query_ieee(query_string)
        if documents is None or len(documents) < 1:
            print 'Error on article with doi = %s' % doi
        else:
            document = documents[0]
            controlled_keywords = find_keyphrases(document, 'controlledterms')
            thesaurus_keywords = find_keyphrases(document, 'thesaurusterms')
            keywords = controlled_keywords.union(thesaurus_keywords)
            for keyword in keywords:
                if keyword in controlled_keywords and keyword in thesaurus_keywords:
                    term_type = DLKeywordTypes.both
                else:
                    term_type = DLKeywordTypes.controlled if keyword in controlled_keywords \
                        else DLKeywordTypes.thesaurus
                k_articles = article_keywords.get(keyword, [])
                k_articles.append((article.article_id, term_type))
                article_keywords[keyword] = k_articles

        print 'Processed article #%s: \"%s\"' % (i, article.title)
        print '-----------------------------------------'

    end_time = datetime.now()
    print 'seconds elapsed: %s' % (end_time-start_time).total_seconds()
    return article_keywords


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


if __name__ == '__main__':
    first = datetime.now()
    # for i in range(0, 9):
    download_ieee_abstracts('cluster analysis', 500, 1)
    second = datetime.now()
    print (second-first).total_seconds()
