# -*- coding: utf-8 -*-
from sklearn.cluster.bicluster import SpectralCoclustering
import numpy as np
from .biclustering import AbstractBiclustering, Bicluster


class SpectralGraphCoclustering(AbstractBiclustering):
    __type__ = 'coclustering'

    def find_disjoint_biclusters(self, biclusters_number=5):
        data = np.asarray_chkfinite(self.matrix)
        data[data == 0] = 0.000001
        coclustering = SpectralCoclustering(n_clusters=biclusters_number, random_state=0)
        coclustering.fit(data)

        biclusters = set()
        for i in range(biclusters_number):
            rows, columns = coclustering.get_indices(i)
            row_set = set(rows)
            columns_set = set(columns)
            if len(row_set) > 0 and len(columns_set) > 0:
                density = self._calculate_box_cluster_density(row_set, columns_set)
                odd_columns = set()
                for column in columns_set:
                    col_density = self._calculate_column_density(column, row_set)
                    if col_density < density / 4:
                        odd_columns.add(column)
                columns_set.difference_update(odd_columns)
                if len(columns_set) == 0:
                    continue

                odd_rows = set()
                for row in row_set:
                    row_density = self._calculate_row_density(row, columns_set)
                    if row_density < density / 4:
                        odd_rows.add(row)
                row_set.difference_update(odd_rows)

                if len(row_set) > 0 and len(columns_set) > 0:
                    density = self._calculate_box_cluster_density(row_set, columns_set)
                    biclusters.add(Bicluster(row_set, columns_set, density))

        return biclusters
