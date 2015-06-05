# -*- coding: utf-8 -*-
import json
from urllib import urlencode
import urllib2

from ..helpers import retriable_n


@retriable_n(20, time_sleep=1)
def download_springer_abstracts(raw_query, number, springer_api_key, start_index=1):
    # constructing query
    query = '("%s" AND type:"Journal")' % raw_query
    params = {'q': query, 'p': number, 's': start_index, 'api_key': springer_api_key}
    query_string = urlencode(params)
    query_url = 'http://api.springer.com/metadata/json?' + query_string

    request = urllib2.Request(query_url)
    response = urllib2.urlopen(request)
    page = response.read()
    response_obj = json.loads(page)

    records = response_obj['records']
    return records
