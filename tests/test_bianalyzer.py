# -*- coding: utf-8 -*
import unittest

from bianalyzer.abstracts import download_abstracts, IEEEKeywordDownloader, DLTermType
from bianalyzer import BianalyzerText
from bianalyzer.keywords import extract_keywords_via_textrank, extract_keywords_via_frequency
from bianalyzer.relevance import construct_similarity_matrix, construct_relevance_matrix
from bianalyzer.biclustering import get_keyword_text_biclusters, get_keyword_biclusters, GreedyBBox, BBox, SpectralGraphCoclustering

springer_api_key = ''  # Put your Springer API key here


class AbstractsTestCase(unittest.TestCase):
    def test_download_ieee(self):
        articles = download_abstracts('IEEE', 'motion recognition', 100)
        self.assertEqual(len(articles), 100)
        for article in articles:
            self.assertEqual(isinstance(article.abstract_text, str), True)

    @unittest.skipIf(springer_api_key is None or springer_api_key == '', 'A user should specify their key')
    def test_download_springer(self):
        articles = download_abstracts('Springer', 'motion recognition', 300, springer_api_key)
        for article in articles:
            self.assertGreater(len(article.abstract_text), 50)
        self.assertEqual(len(articles), 300)
        for article in articles:
            self.assertIsInstance(article.abstract_text, unicode or str)

    def test_ieee_keywords_download(self):
        articles = download_abstracts('IEEE', 'motion recognition', 10)
        downloader = IEEEKeywordDownloader(articles, DLTermType.controlled)
        keywords = downloader.download_ieee_keywords()
        self.assertEqual((len(keywords) > 0), True)


class KeywordsTestCase(unittest.TestCase):
    def setUp(self):
        super(KeywordsTestCase, self).setUp()
        texts = ['This paper focuses on the development of an effective cluster validity measure with outlier detection and cluster merging algorithms for support vector clustering (SVC)',
                 'In a multi-cluster tool, there may be both single and dual-arm cluster tools. Such a multi-cluster tool is called hybrid multi-cluster tool',
                 'Fuel maps are critical tools for spatially explicit fire simulation and analysis. Many diverse techniques have been used to create spatial fuel data products including field assessment, association, remote sensing, and biophysical modeling.']
        b_texts = [BianalyzerText(t) for t in texts]
        self.texts = b_texts

    def test_textrank(self):
        keywords = extract_keywords_via_textrank(self.texts, window_size=3, keyword_limit=10, frequency_filter=False,
                                                 stemming_filter=False)
        self.assertTrue(len(keywords) >= 10)

    def test_frequency(self):
        keywords = extract_keywords_via_frequency(self.texts, max_freq=50)
        self.assertTrue(len(keywords) > 0)


class RelevanceTestCase(unittest.TestCase):
    def setUp(self):
        super(RelevanceTestCase, self).setUp()
        texts = ['This paper focuses on the development of an effective cluster validity measure with outlier detection and cluster merging algorithms for support vector clustering (SVC)',
                 'In a multi-cluster tool, there may be both single and dual-arm cluster tools. Such a multi-cluster tool is called hybrid multi-cluster tool',
                 'Fuel maps are critical tools for spatially explicit fire simulation and analysis. Many diverse techniques have been used to create spatial fuel data products including field assessment, association, remote sensing, and biophysical modeling.']
        b_texts = [BianalyzerText(t) for t in texts]
        self.texts = b_texts
        self.keywords = ['development', 'cluster validity', 'measure', 'simulation', 'tools', 'cluster', 'fuel']

    def test_relevance_matrix(self):
        matrix = construct_relevance_matrix(self.keywords, self.texts, 'bm25').matrix
        self.assertEqual(len(matrix), len(self.keywords))
        self.assertEqual(len(matrix[0]), len(self.texts))
        for row in matrix:
            row_max = max(row)
            self.assertGreater(row_max, 0.0)

    def test_similarity_matrix(self):
        rel_matrix = construct_relevance_matrix(self.keywords, self.texts, 'frequency')
        sim_matrix = construct_similarity_matrix(rel_matrix, 0.1).matrix
        self.assertEqual(len(sim_matrix), len(self.keywords))
        self.assertEqual(len(sim_matrix[0]), len(self.keywords))


class BiclusteringTestCase(unittest.TestCase):
    def setUp(self):
        texts = ['This paper focuses on the development of an effective cluster validity measure with outlier detection and cluster merging algorithms for support vector clustering (SVC)',
                 'In a multi-cluster tool, there may be both single and dual-arm cluster tools. Such a multi-cluster tool is called hybrid multi-cluster tool',
                 'Fuel maps are critical tools for spatially explicit fire simulation and analysis. Many diverse techniques have been used to create spatial fuel data products including field assessment, association, remote sensing, and biophysical modeling.']
        b_texts = [BianalyzerText(t) for t in texts]
        self.texts = b_texts
        self.keywords = ['development', 'cluster validity', 'measure', 'simulation', 'tools', 'cluster', 'fuel']
        self.relevance_matrix = construct_relevance_matrix(self.keywords, self.texts, 'tf-idf')
        self.similarity_matrix = construct_similarity_matrix(self.relevance_matrix, 0.2)

    def test_relevance_biclustering(self):
        result = get_keyword_text_biclusters(self.relevance_matrix, BBox)
        self.assertGreater(len(result.biclusters), 0)
        result = get_keyword_text_biclusters(self.relevance_matrix, GreedyBBox)
        self.assertGreater(len(result.biclusters), 0)
        result = get_keyword_text_biclusters(self.relevance_matrix, SpectralGraphCoclustering, biclusters_number=5)
        self.assertGreater(len(result.biclusters), 0)

    def test_similarity_biclustering(self):
        result = get_keyword_biclusters(self.similarity_matrix, BBox)
        self.assertGreater(len(result.biclusters), 0)
        result = get_keyword_biclusters(self.similarity_matrix, GreedyBBox)
        self.assertGreater(len(result.biclusters), 0)
        result = get_keyword_biclusters(self.similarity_matrix, SpectralGraphCoclustering, biclusters_number=5)
        self.assertGreater(len(result.biclusters), 0)