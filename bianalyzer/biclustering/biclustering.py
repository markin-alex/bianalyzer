# -*- coding: utf-8 -*-

EPS = 0.0000001  # for floating point values comparison


class Bicluster(object):
    def __init__(self, row_set, column_set, density):
        self.row_set = row_set
        self.column_set = column_set
        self.density = density  # round(density, 3)
        self.g_value = density * density * len(column_set) * len(row_set)

    def __eq__(self, another_bicluster):
        return (self.density - another_bicluster.density < EPS) and \
               (self.row_set == another_bicluster.row_set) and (self.column_set == another_bicluster.column_set)

    def __hash__(self):
        return hash(round(self.g_value, 5))

    @staticmethod
    def empty_bicluster():
        return Bicluster(set(), set(), 0.0)


class AbstractBiclustering:  # Not for instantiation!
    __type__ = 'biclustering'

    def __init__(self, matrix, lambda0=0.0):
        self.matrix = matrix
        self.intermediate_biclusters = {}
        self.total_iterations = 0
        self.saved_operations = 0
        if lambda0 > 0:
            self._decrease_overall_density(lambda0)

    def find_biclusters(self, initial_threshold=0.5):
        biclusters = set()

        self.intermediate_biclusters = {}  # for memoization

        for row_ind in range(len(self.matrix)):
            new_bicluster = self.find_bicluster(row_ind, initial_threshold)
            if new_bicluster in biclusters or new_bicluster.density <= 0:
                continue
            biclusters.add(new_bicluster)

        return biclusters

    def find_bicluster(self, row, initial_threshold=0.5):
        pass

    def _decrease_overall_density(self, lambda0):
        assert lambda0 >= 0.0
        assert lambda0 <= 1.0
        for row in self.matrix:
            for col_ind in range(len(row)):
                row[col_ind] = row[col_ind] - lambda0

    def _calculate_box_cluster_density(self, row_set, column_set):
        n = len(row_set)
        total_row_density = 0.0
        for row in row_set:
            total_row_density += self._calculate_row_density(row, column_set)
        density = total_row_density / n

        return density

    def _calculate_row_density(self, row_index, column_set):
        row = self.matrix[row_index]
        m = len(column_set)
        row_sum = 0
        for j in column_set:
            row_sum += row[j]
        density = float(row_sum) / m

        return density

    def _calculate_column_density(self, column_index, row_set):
        n = len(row_set)
        column_sum = 0
        for i in row_set:
            column_sum += self.matrix[i][column_index]
        density = float(column_sum) / n

        return density


class GreedyBBox(AbstractBiclustering):

    def find_bicluster(self, row, initial_threshold=0.5):
        row_set = set()
        row_set.add(row)

        # setting up an initial column set
        initial_row_max = float(max(self.matrix[row]))

        if initial_row_max <= 0.0 + EPS:
            return Bicluster.empty_bicluster()

        column_set = set()
        for j in range(len(self.matrix[row])):
            if self.matrix[row][j] >= initial_row_max * initial_threshold:
                column_set.add(j)

        box_density = self._calculate_box_cluster_density(row_set, column_set)
        g_value = box_density * box_density * len(row_set) * len(column_set)

        while True:
            new_rows = set()
            for row_ind in range(len(self.matrix)):
                if row_ind not in row_set:
                    row_density = self._calculate_row_density(row_ind, column_set)
                    if row_density >= box_density / 2:
                        new_rows.add(row_ind)

            updated_row_set = row_set.union(new_rows)

            odd_columns = set()
            for column_ind in range(len(self.matrix[0])):
                if column_ind in column_set:
                    column_density = self._calculate_column_density(column_ind, updated_row_set)
                    if column_density < box_density / 2:
                        odd_columns.add(column_ind)

            updated_column_set = column_set.difference(odd_columns)
            new_box_density = self._calculate_box_cluster_density(updated_row_set, updated_column_set)
            new_g_value = new_box_density * new_box_density * len(updated_row_set) * len(updated_column_set)
            if new_g_value <= g_value:
                break

            row_set.update(new_rows)
            column_set.difference_update(odd_columns)
            box_density = new_box_density
            g_value = new_g_value

        return Bicluster(row_set, column_set, box_density)


def count_collisions(d):
    unique_hashes = set()
    collisions = 0
    for key in d:
        key_hash = hash(key)
        if key_hash in unique_hashes:
            collisions += 1
        else:
            unique_hashes.add(key_hash)

    return collisions