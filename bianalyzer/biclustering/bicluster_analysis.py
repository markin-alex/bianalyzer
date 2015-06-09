# -*- coding: utf-8 -*-

from .biclustering import AbstractBiclustering
from .matrices import get_matrix_squared_sum, get_residuals_matrix
from ..errors import InvalidArgumentError
from ..helpers import jaccard_set_similarity


class BiclusteringResult:
    def __init__(self, biclusters, total_rows_num, total_columns_num, matrix_squared_sum, residuals):
        self.biclusters = biclusters
        self.total_rows_num = total_rows_num
        self.total_columns_num = total_columns_num
        self.matrix_squared_sum = round(matrix_squared_sum, 3)
        self.residuals = round(residuals, 3)
        if matrix_squared_sum > 0:
            self.residuals_portion = round(residuals / matrix_squared_sum, 3)
        else:
            self.residuals_portion = 0


def find_biclusters(matrix, biclustering_algorithm, lambda0=0.0, biclusters_number=100):
    if not issubclass(biclustering_algorithm, AbstractBiclustering):
        raise InvalidArgumentError("biclustering_algorithm", biclustering_algorithm,
                                   "Must be a subclass of AbstractBiclustering")

    biclustering = biclustering_algorithm(matrix, lambda0)
    if biclustering.__type__ == AbstractBiclustering.__type__:
        biclusters = biclustering.find_biclusters()
    else:
        biclusters = biclustering.find_disjoint_biclusters(biclusters_number)

    biclusters = sorted(biclusters, key=lambda x: x.g_value, reverse=True)
    biclusters = filter_biclusters(biclusters)

    residuals_matrix = get_residuals_matrix(matrix, biclusters)
    residuals = get_matrix_squared_sum(residuals_matrix)
    matrix_squared_sum = get_matrix_squared_sum(matrix)
    result = BiclusteringResult(biclusters, len(matrix), len(matrix[0]), matrix_squared_sum, residuals)
    print 'Residual portion: %.2f' % result.residuals_portion
    print 'Total number of biclusters: %s' % len(result.biclusters)
    return result


def filter_biclusters(biclusters, similarity_threshold=0.7):
    final_biclusters = []
    for bicluster in biclusters:
        found = False
        for i, final_bicluster in enumerate(final_biclusters):
            rows_similarity = jaccard_set_similarity(bicluster.row_set, final_bicluster.row_set)
            columns_similarity = jaccard_set_similarity(bicluster.column_set, final_bicluster.column_set)
            if rows_similarity >= similarity_threshold and columns_similarity >= similarity_threshold:
                found = True
                if bicluster.g_value > final_bicluster.g_value:
                    final_biclusters[i] = bicluster
        if not found:
            final_biclusters.append(bicluster)

    print 'filtered out biclusters: %s' % (len(biclusters) - len(final_biclusters))
    return final_biclusters
