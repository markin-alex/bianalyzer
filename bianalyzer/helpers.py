# -*- coding: utf-8 -*-
from functools import wraps
import time
import re

from .errors import InvalidArgumentError
from .texts import BianalyzerText


def retriable_n(retry_count=3, time_sleep=0.2, exceptions=(Exception,)):
    def retriable_n_deco(func):
        @wraps(func)
        def wrapper(*args, **kw):
            for i in range(1, retry_count):
                try:
                    return func(*args, **kw)
                except Exception, e:
                    if isinstance(e, exceptions):
                        print ('%s(*%s, **%s) try %i failed, retrying: %s' % (func.__name__, args, kw, i, e))
                        time.sleep(time_sleep)
                    else:
                        raise
            else:
                return func(*args, **kw)
        return wrapper
    return retriable_n_deco


def check_text_collection(texts, raise_error=True):
    for text in texts:
        is_bianalyzer_text = isinstance(text, BianalyzerText)
        if not is_bianalyzer_text:
            if raise_error:
                raise InvalidArgumentError('texts', text, 'All texts in the collection must be of type BianalyzerText')
            return False

    return True


def remove_html_tags(text, unsafe=True):

        def extract_value(match_obj):
            return match_obj.group('value')

        def remove_tags(t):
            tag_pattern = '<(?P<tag>\w+)>(?P<value>.*?)</(?P=tag)>'
            result = re.sub(tag_pattern, extract_value, t)
            if unsafe:
                result = re.sub('<[^<>]*>', '', result)
            return result

        new_text = remove_tags(text)
        while len(new_text) < len(text):
            text = new_text
            new_text = remove_tags(text)

        return text


def jaccard_set_similarity(set1, set2):
    set_union = set1.union(set2)
    if len(set_union) > 0:
        similarity = float(len(set1.intersection(set2))) / len(set_union)
        return similarity
    else:
        return 0.0


def mbi_set_similarity(set1, set2):
    set_intersection = float(len(set1.intersection(set2)))
    if len(set1) > 0 and len(set2) > 0:
        similarity = (set_intersection / len(set1) + set_intersection / len(set2)) / 2
        return similarity
    else:
        return 0.0


def calculate_row_density(row_index, matrix):
        row = matrix[row_index]
        m = len(matrix[row_index])
        row_sum = 0
        for j in range(m):
            row_sum += row[j]
        density = float(row_sum) / m

        return density


def calculate_column_density(column_index, matrix):
    n = len(matrix)
    column_sum = 0
    for i in range(n):
        column_sum += matrix[i][column_index]
    density = float(column_sum) / n

    return density


def construct_similarity_matrix_via_profiles(keywords, relevance_profiles):
    keyword_similarity_matrix = []
    total_sum = 0.0
    for row, keyword1 in enumerate(keywords):
        keyword_similarity_matrix.append([])
        row_sum = 0
        for col, keyword2 in enumerate(keywords):
            similarity = 0.0
            if len(relevance_profiles[row]) > 0:
                similarity = float(len(relevance_profiles[row].intersection(relevance_profiles[col])))
                similarity /= len(relevance_profiles[row])
                if col != row:
                    row_sum += similarity
                    total_sum += similarity
            keyword_similarity_matrix[row].append(similarity)

        # print "keyword '%s' - row sum: %s; mean: %s" % (keyword1, row_sum, row_sum / len(relevant_keywords))
        keyword_similarity_matrix[row][row] = row_sum / len(keywords)
        total_sum += keyword_similarity_matrix[row][row]

    # for row in keyword_similarity_matrix:
    #     s = ''
    #     for val in row:
    #         s += '%5s' % round(val, 2)
    #     print s

    total_average = total_sum / (len(keywords) * len(keywords))
    print 'average value in the matrix: %s' % total_average

    return keyword_similarity_matrix