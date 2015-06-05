# -*- coding: utf-8 -*-


class DownloadingConfig:
    MAX_ARTICLES_PER_QUERY = 10000
    MIN_ABSTRACT_SIZE = 30  # skip the articles with abstracts containing less than MIN_ABSTRACT_SIZE words

    IEEE_MAX_RECORDS = 1000  # IEEE API can't return more than IEEE_MAX_RECORDS records per request

    SPRINGER_MAX_RECORDS = 100  # Springer API can't return more than SPRINGER_MAX_RECORDS records per request
