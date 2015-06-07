# -*- coding: utf-8 -*-
from east import utils
from east.asts import base

from ..errors import InvalidArgumentError
from .relevance_metrics import tf_idf, bm25, keyword_frequency


class RelevanceMatrix:
    def __init__(self, keywords, texts, matrix, max_score=None):
        self.keywords = keywords
        self.texts = texts
        self.matrix = matrix
        self.max_relevance_score = max_score
        if max_score is None:
            self._find_max_score()

    def _find_max_score(self):
        max_score = -100000
        for row in self.matrix:
            for val in row:
                if val > max_score:
                    max_score = max_score
        self.max_relevance_score = max_score


class RelevanceMetric:
    tf_idf = "tf-idf"
    bm25 = "bm25"
    ast = "ast"
    frequency = "frequency"
    normalized_frequency = "normalized_frequency"

relevance_metrics = (
    RelevanceMetric.tf_idf,
    RelevanceMetric.bm25,
    RelevanceMetric.ast,
    RelevanceMetric.frequency,
    RelevanceMetric.normalized_frequency
)


def construct_relevance_matrix(keywords, bianalyzer_texts, relevance_metric, query=False, **metric_params):
    if relevance_metric not in relevance_metrics:
        raise InvalidArgumentError("relevance_metric", relevance_metric, "Such relevance metric is not supported")

    collection_length = len(bianalyzer_texts)
    average_doc_length = calculate_average_text_length(bianalyzer_texts)
    print 'average text length: %s' % average_doc_length

    # AST only
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
        kw_words = keyword.split()
        relevance_matrix.append([])

        # TF-IDF and BM25 preparation (for IDF calculation)
        if relevance_metric == RelevanceMetric.tf_idf or relevance_metric == RelevanceMetric.bm25:
            kw_occurrences = 0  # frequency as a whole
            kw_word_occurrences = [0 for _ in range(len(kw_words))]  # frequency for each word separately
            for bianalyzer_text in bianalyzer_texts:
                if keyword_frequency(bianalyzer_text, keyword) > 0:
                    kw_occurrences += 1
                for j, word in enumerate(kw_words):
                    if keyword_frequency(bianalyzer_text, word) > 0:
                        kw_word_occurrences[j] += 1

        for (j, bianalyzer_text) in enumerate(bianalyzer_texts):
            relevance_score = 0
            if relevance_metric == RelevanceMetric.tf_idf:
                if query:
                    for k, word in enumerate(kw_words):
                        relevance_score += tf_idf(word, collection_length, kw_word_occurrences[k], bianalyzer_text)
                else:
                    relevance_score = tf_idf(keyword, collection_length, kw_occurrences,
                                             bianalyzer_text)
            elif relevance_metric == RelevanceMetric.bm25:
                if query:
                    for k, word in enumerate(kw_words):
                        relevance_score += bm25(word, collection_length, kw_word_occurrences[k], average_doc_length,
                                                bianalyzer_text, **metric_params)
                else:
                    relevance_score = bm25(keyword, collection_length, kw_occurrences,
                                           average_doc_length, bianalyzer_text)
            elif relevance_metric == RelevanceMetric.ast:
                if keyword_frequency(bianalyzer_text, keyword) > 0.0 and text_asts[j] is not None:
                    relevance_score = text_asts[j].score(keyword.upper())
            elif relevance_metric == RelevanceMetric.frequency:
                relevance_score = float(keyword_frequency(bianalyzer_text, keyword))
            elif relevance_metric == RelevanceMetric.normalized_frequency:
                relevance_score = float(keyword_frequency(bianalyzer_text, keyword)) / bianalyzer_text.text_length

            if relevance_score > max_score:
                max_score = relevance_score

            relevance_matrix[i].append(relevance_score)

    print 'max relevance score in the matrix: %.3f' % max_score
    return RelevanceMatrix(keywords, bianalyzer_texts, relevance_matrix, max_score)


def calculate_average_text_length(collection):
    length_sum = 0.0
    for text in collection:
        length_sum += text.text_length

    return float(length_sum) / len(collection)
