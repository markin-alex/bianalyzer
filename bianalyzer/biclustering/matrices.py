# -*- coding: utf-8 -*-


def get_matrix_squared_sum(matrix):
    squared_sum = 0.0
    for row in matrix:
        for val in row:
            squared_sum += val * val

    return squared_sum


def get_residuals_matrix(matrix, biclusters):
    residuals = [row[:] for row in matrix]
    for bicluster in biclusters:
        for row in bicluster.row_set:
            for column in bicluster.column_set:
                res = matrix[row][column] - bicluster.density
                if res < residuals[row][column]:
                    residuals[row][column] = res
    return residuals
