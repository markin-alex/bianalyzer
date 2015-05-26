# -*- coding: utf-8 -*-

from .bicluster_analysis import find_biclusters


class KeywordBicluster:
    def __init__(self, keyword_rows, keyword_columns, similarity_matrix, density, g_value):
        self.keyword_rows = keyword_rows
        self.keyword_columns = keyword_columns
        self.similarity_matrix = similarity_matrix
        self.density = density
        self.g_value = g_value


def get_keyword_biclusters(similarity_matrix, biclustering_algorithm,
                           max_biclusters_number=1000, lambda0=0.0):
    # TODO: is filtering based on size needed?

    matrix = similarity_matrix.matrix
    keywords = similarity_matrix.keywords
    biclustering_result = find_biclusters(matrix, biclustering_algorithm, lambda0)

    keyword_biclusters = []
    for bicluster in biclustering_result.biclusters:
        print '----------------------------'
        print 'new bicluster'

        keyword_rows = []
        first_set = ''
        for row in bicluster.row_set:
            first_set += '%s, ' % keywords[row]
            keyword_rows.append(keywords[row])
        print first_set

        keyword_columns = []
        second_set = ''
        for col in bicluster.column_set:
            second_set += '%s, ' % keywords[col]
            keyword_columns.append(keywords[col])
        print second_set

        print 'density: %s' % bicluster.density
        print 'row set len: %s' % len(bicluster.row_set)
        print 'column set len: %s' % len(bicluster.column_set)
        print 'g-value: %s' % round(bicluster.g_value, 2)

        bicluster_matrix = []
        for (i, row) in enumerate(bicluster.row_set):
            bicluster_matrix.append([])
            s = ''
            for col in bicluster.column_set:
                s += '%6s' % round(matrix[row][col], 2)
                bicluster_matrix[i].append(round(matrix[row][col], 2))
            print s

        keyword_biclusters.append(KeywordBicluster(keyword_rows, keyword_columns, bicluster_matrix,
                                                   round(bicluster.density, 2), round(bicluster.g_value, 2)))

    # keyword_biclusters = keyword_biclusters[:max_biclusters_number]
    biclustering_result.biclusters = keyword_biclusters
    return biclustering_result
