# -*- coding: utf-8 -*-
from datetime import datetime
import json
from urllib import urlencode
import urllib2

from ..helpers import retriable_n
from .downloading_config import DownloadingConfig


@retriable_n(20, time_sleep=1)
def download_springer_abstracts(raw_query, number, start_index=1):
    # constructing query
    query = '("%s" AND type:"Journal")' % raw_query
    params = {'q': raw_query, 'p': number, 's': start_index, 'api_key': DownloadingConfig.SPRINGER_API_KEY}
    query_string = urlencode(params)
    query_url = 'http://api.springer.com/metadata/json?' + query_string
    print query_url

    request = urllib2.Request(query_url)
    response = urllib2.urlopen(request)
    page = response.read()
    response_obj = json.loads(page)

    records = response_obj['records']
    return records


if __name__ == '__main__':
    first = datetime.now()
    #for i in range(0, 9):
    download_springer_abstracts('cluster analysis', 500, 1)
    second = datetime.now()
    print (second-first).total_seconds()
