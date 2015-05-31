# -*- coding: utf-8 -*-
from east import utils
from east.asts import base

from ..errors import InvalidArgumentError
from .relevance_metrics import tf_idf, bm25, keyword_frequency


class RelevanceMatrix:
    def __init__(self, keywords, texts, matrix, max_score):
        self.keywords = keywords
        self.texts = texts
        self.matrix = matrix
        self.max_relevance_score = max_score


class RelevanceMetric:
    tf_idf = "TF IDF"
    bm25 = "BM25"
    ast = "AST"
    naive = "Naive"

relevance_metrics = (
    RelevanceMetric.tf_idf,
    RelevanceMetric.bm25,
    RelevanceMetric.ast,
    RelevanceMetric.naive
)


def construct_relevance_matrix(keywords, bianalyzer_texts, relevance_metric, params=None):
    if relevance_metric not in relevance_metrics:
        raise InvalidArgumentError("relevance_metric", relevance_metric, "Such relevance metric is not supported")
    if params is not None and not isinstance(params, dict):
        raise InvalidArgumentError("params", params, "Should be a dictionary!")
    elif params is None:
        params = {}

    collection_length = len(bianalyzer_texts)
    average_doc_length = calculate_average_text_length(bianalyzer_texts)
    print 'average text length: %s' % average_doc_length

    # ast only
    text_asts = []
    if relevance_metric == RelevanceMetric.ast:
        for bianalyzer_text in bianalyzer_texts:
            try:
                short_strings_collection = utils.text_to_strings_collection(bianalyzer_text.text)
            except UnicodeEncodeError:
                text_asts.append(None)
                continue
            ast = base.AST.get_ast(short_strings_collection)
            text_asts.append(ast)

    relevance_matrix = []
    max_score = 0
    for (i, keyword) in enumerate(keywords):
        relevance_matrix.append([])
        if relevance_metric == RelevanceMetric.tf_idf or relevance_metric == RelevanceMetric.bm25:
            kw_occurrences = 0
            for bianalyzer_text in bianalyzer_texts:
                if keyword_frequency(bianalyzer_text, keyword) > 0:
                    kw_occurrences += 1

        for (j, bianalyzer_text) in enumerate(bianalyzer_texts):
            relevance_score = 0
            if relevance_metric == RelevanceMetric.tf_idf:
                relevance_score = tf_idf(collection_length, kw_occurrences,
                                         bianalyzer_text, keyword)
            elif relevance_metric == RelevanceMetric.bm25:
                relevance_score = bm25(collection_length, kw_occurrences,
                                       average_doc_length, bianalyzer_text, keyword)
            elif relevance_metric == RelevanceMetric.ast:
                if keyword_frequency(bianalyzer_text, keyword) > 0.0 and text_asts[j] is not None:
                    relevance_score = text_asts[j].score(keyword.upper())
            elif relevance_metric == RelevanceMetric.naive:
                relevance_score = float(keyword_frequency(bianalyzer_text, keyword)) / bianalyzer_text.text_length

            if relevance_score > max_score:
                max_score = relevance_score

            relevance_matrix[i].append(relevance_score)

    return RelevanceMatrix(keywords, bianalyzer_texts, relevance_matrix, max_score)


def calculate_average_text_length(collection):
    length_sum = 0.0
    for text in collection:
        length_sum += text.text_length

    return float(length_sum) / len(collection)
