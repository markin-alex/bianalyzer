# -*- coding: utf-8 -*-
from ..errors import InvalidArgumentError, MissingArgumentError
from .downloading_config import DownloadingConfig
from .ieee_downloader import download_ieee_abstracts
from .springer_downloader import download_springer_abstracts
from .article import Article

SUPPORTED_SOURCE_LIST = ['IEEE', 'Springer']


class DownloadingError(Exception):
    def __init__(self, message=''):
        super(DownloadingError, self).__init__('Could not start downloading the abstracts; %s' % message)


def download_abstracts(source, raw_query, number, springer_api_key=None):
    if number > DownloadingConfig.MAX_ARTICLES_PER_QUERY:
        raise InvalidArgumentError('number', number, message='cannot handle more than %s articles at once'
                                                             % DownloadingConfig.MAX_ARTICLES_PER_QUERY)
    if source not in SUPPORTED_SOURCE_LIST:
        raise InvalidArgumentError('source', source, 'Supported sources are %s' % SUPPORTED_SOURCE_LIST)
    if source == 'Springer' and springer_api_key is None:
        raise MissingArgumentError('springer_api_key', 'You should indicate the API Key '
                                                       'in order to download articles from Springer Library')

    raw_query = raw_query.strip()

    articles = []  # here we will maintain a list of all downloaded records (articles)

    start_index = 1
    left_number = number
    max_records = DownloadingConfig.IEEE_MAX_RECORDS if source == 'IEEE' else DownloadingConfig.SPRINGER_MAX_RECORDS
    while left_number > 0:
        real_number = left_number if left_number < max_records else max_records

        if source == 'IEEE':
            new_records = download_ieee_abstracts(raw_query, real_number, start_index=start_index)
        elif source == 'Springer':
            new_records = download_springer_abstracts(raw_query, real_number, springer_api_key, start_index=start_index)

        if (new_records is None or len(new_records) == 0) and len(articles) == 0:
            raise DownloadingError()

        for record in new_records:
            start_index += 1
            try:
                article = Article(record, source)
                if len(article.abstract_text) > 50:
                    articles.append(article)
                    left_number -= 1
            except Exception, e:
                # print 'could not process document: %s' % e
                pass

    return articles