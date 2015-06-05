# -*- coding: utf-8 -*-

from .biclustering import Bicluster, AbstractBiclustering


class BBox(AbstractBiclustering):

    def find_bicluster(self, initial_row, initial_threshold=0.5, memoization=False):
        row_set = set()
        row_set.add(initial_row)

        # setting up an initial column set
        initial_row_max = float(max(self.matrix[initial_row]))

        eps = 0.000001
        if initial_row_max <= 0.0 + eps:
            return Bicluster.empty_bicluster()

        column_set = set()
        for j in range(len(self.matrix[initial_row])):
            if self.matrix[initial_row][j] >= initial_row_max * initial_threshold:
                column_set.add(j)

        box_density = self._calculate_box_cluster_density(row_set, column_set)
        g_value = box_density * box_density * len(row_set) * len(column_set)

        previous_biclusters = []
        while True:
            # ------------Memoization--------------
            if memoization:
                current_bicluster = Bicluster(row_set, column_set, box_density)
                final_bicluster, saved_num = self.intermediate_biclusters.get(current_bicluster, (None, 0))
                if final_bicluster is not None:
                    for bicluster in previous_biclusters:
                        self.intermediate_biclusters[bicluster] = (final_bicluster, saved_num)
                    return final_bicluster
                previous_biclusters.append(current_bicluster)
            # -------------------------------------

            n = len(row_set)
            m = len(column_set)

            max_r_g = -1
            max_r_density = -1
            max_row = -1
            for row_ind in range(len(self.matrix)):
                density = self._calculate_row_density(row_ind, column_set)
                r_density = 0
                d = 1
                if row_ind in row_set and n > 1:
                    r_density = (box_density * n - density) / (n - 1)
                    d = -1
                elif row_ind not in row_set:
                    r_density = (box_density * n + density) / (n + 1)
                r_g = r_density * r_density * (n + d) * m
                if r_g > max_r_g:
                    max_r_g = r_g
                    max_r_density = r_density
                    max_row = row_ind

            max_c_g = -1
            max_c_density = -1
            max_col = -1
            for column_ind in range(len(self.matrix[0])):
                density = self._calculate_column_density(column_ind, row_set)
                c_density = 0
                d = 1
                if column_ind in column_set and m > 1:
                    c_density = (box_density * m - density) / (m - 1)
                    d = -1
                elif column_ind not in column_set:
                    c_density = (box_density * m + density) / (m + 1)
                c_g = c_density * c_density * (m + d) * n
                if c_g > max_c_g:
                    max_c_g = c_g
                    max_c_density = c_density
                    max_col = column_ind

            if max_c_g <= g_value and max_r_g <= g_value:
                break

            if max_c_g > max_r_g:
                g_value = max_c_g
                box_density = max_c_density
                if max_col in column_set:
                    column_set.remove(max_col)
                else:
                    column_set.add(max_col)
            else:
                g_value = max_r_g
                box_density = max_r_density
                if max_row in row_set:
                    row_set.remove(max_row)
                else:
                    row_set.add(max_row)

        final_bicluster = Bicluster(row_set, column_set, box_density)
        # print 'row #%s, finished, processed: %s biclusters' % (initial_row, len(previous_biclusters))
        if memoization:
            prev_num = len(previous_biclusters)
            self.total_iterations += prev_num
            for i, bicluster in enumerate(previous_biclusters):
                self.intermediate_biclusters[bicluster] = (final_bicluster, prev_num - i)

        return final_bicluster
