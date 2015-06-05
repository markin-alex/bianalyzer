# -*- coding: utf-8 -*-
from ..helpers import construct_similarity_matrix_via_profiles


class SimilarityMatrix:
    def __init__(self, keywords, matrix):
        self.keywords = keywords
        self.matrix = matrix


def construct_similarity_matrix(relevance_matrix, relevance_threshold=0.2):
    """
    Constructs keyword similarity matrix by the given relevance_matrix
    NOTE: final similarity matrix may contain not all the keywords (only those that are highly relevant to
    at least one of the texts)
    :param relevance_matrix: instance of SimilarityMatrix
    :param relevance_threshold: a value in range [0, 1)
    :return: instance of a class SimilarityMatrix
    """

    # create relevance profiles
    relevance_profiles = []
    keywords = relevance_matrix.keywords
    max_score = relevance_matrix.max_relevance_score
    print 'max score: %s' % max_score
    real_threshold = relevance_threshold * max_score
    relevant_keywords = []
    for (i, keyword) in enumerate(keywords):
        keyword_row = relevance_matrix.matrix[i]
        relevance_profile = set([i for i, val in enumerate(keyword_row) if val >= real_threshold])
        if len(relevance_profile) > 0:
            print 'keyword: %s, relevance profile size: %s' % (keyword, len(relevance_profile))
            relevant_keywords.append(keyword)
            relevance_profiles.append(relevance_profile)

    keyword_similarity_matrix = construct_similarity_matrix_via_profiles(relevant_keywords, relevance_profiles)
    return SimilarityMatrix(relevant_keywords, keyword_similarity_matrix)
