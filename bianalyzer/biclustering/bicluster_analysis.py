# -*- coding: utf-8 -*-

from .biclustering import AbstractBiclustering
from .matrices import get_matrix_scatter, get_residuals_matrix
from ..errors import InvalidArgumentError


class BiclusteringResult:
    def __init__(self, biclusters, total_rows_num, total_columns_num, matrix_scatter, residuals):
        self.biclusters = biclusters
        self.total_rows_num = total_rows_num
        self.total_columns_num = total_columns_num
        self.matrix_scatter = round(matrix_scatter, 3)
        self.residuals = round(residuals, 3)
        self.residuals_portion = round(residuals / matrix_scatter, 3)


def find_biclusters(matrix, biclustering_algorithm, lambda0=0.0, max_biclusters_number=100):
    if not issubclass(biclustering_algorithm, AbstractBiclustering):
        raise InvalidArgumentError("biclustering_algorithm", biclustering_algorithm,
                                   "Must be a subclass of AbstractBiclustering")

    biclustering = biclustering_algorithm(matrix, lambda0)
    if biclustering.__type__ == AbstractBiclustering.__type__:
        biclusters = biclustering.find_biclusters()
    else:
        biclusters = biclustering.find_coclusters(max_biclusters_number)

    biclusters = sorted(biclusters, key=lambda x: x.g_value, reverse=True)
    biclusters = filter_biclusters(biclusters)

    residuals_matrix = get_residuals_matrix(matrix, biclusters)
    residuals = get_matrix_scatter(residuals_matrix)
    matrix_scatter = get_matrix_scatter(matrix)
    result = BiclusteringResult(biclusters, len(matrix), len(matrix[0]), matrix_scatter, residuals)
    return result


def filter_biclusters(biclusters, similarity_threshold=0.7):
    final_biclusters = []
    for bicluster in biclusters:
        found = False
        for i, final_bicluster in enumerate(final_biclusters):
            rows_similarity = set_similarity(bicluster.row_set, final_bicluster.row_set)
            columns_similarity = set_similarity(bicluster.column_set, final_bicluster.column_set)
            if rows_similarity >= similarity_threshold and columns_similarity >= similarity_threshold:
                found = True
                if bicluster.g_value > final_bicluster.g_value:
                    final_biclusters[i] = bicluster
        if not found:
            final_biclusters.append(bicluster)

    print 'filtered out biclusters: %s' % (len(biclusters) - len(final_biclusters))
    return final_biclusters


def set_similarity(set1, set2):
    set_union = set1.union(set2)
    if len(set_union) > 0:
        similarity = float(len(set1.intersection(set2))) / len(set_union)
        return similarity
    else:
        return 0.0