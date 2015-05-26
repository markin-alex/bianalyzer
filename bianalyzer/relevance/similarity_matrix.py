# -*- coding: utf-8 -*-


class SimilarityMatrix:
    def __init__(self, keywords, matrix):
        self.keywords = keywords
        self.matrix = matrix


def construct_similarity_matrix(relevance_matrix, relevance_threshold=0.2):
    """
    Constructs keyword similarity matrix by given relevance_matrix
    NOTE: final similarity matrix may contain not all the keywords (only those that are highly relevant to
    at least one of the texts)
    :param relevance_matrix: instance of SimilarityMatrix
    :param relevance_threshold: a value in range [0, 1)
    :return: instance of SimilarityMatrix
    """

    # create relevance profiles
    relevance_profiles = []
    keywords = relevance_matrix.keywords
    max_score = relevance_matrix.max_relevance_score
    print 'max score: %s' % max_score
    real_threshold = relevance_threshold * max_score
    relevant_keywords = []
    for (i, keyword) in enumerate(keywords):
        keyword_row = relevance_matrix.matrix[i]
        relevance_profile = set([val for val in keyword_row if val >= real_threshold])
        if len(relevance_profile) > 0:
            print 'keyword: %s, relevance profile size: %s' % (keyword, len(relevance_profile))
            relevant_keywords.append(keyword)
            relevance_profiles.append(relevance_profile)

    keyword_similarity_matrix = construct_matrix_via_profiles(relevant_keywords, relevance_profiles)
    return SimilarityMatrix(relevant_keywords, keyword_similarity_matrix)


def construct_matrix_via_profiles(keywords, relevance_profiles):
    keyword_similarity_matrix = []
    total_sum = 0.0
    for row, keyword1 in enumerate(keywords):
        keyword_similarity_matrix.append([])
        row_sum = 0
        for col, keyword2 in enumerate(keywords):
            similarity = 0.0
            if len(relevance_profiles[row]) > 0:
                similarity = float(len(relevance_profiles[row].intersection(relevance_profiles[col])))
                similarity /= len(relevance_profiles[row])
                if col != row:
                    row_sum += similarity
                    total_sum += similarity
            keyword_similarity_matrix[row].append(similarity)

        # print "keyword '%s' - row sum: %s; mean: %s" % (keyword1, row_sum, row_sum / len(relevant_keywords))
        keyword_similarity_matrix[row][row] = row_sum / len(keywords)
        total_sum += keyword_similarity_matrix[row][row]

    for row in keyword_similarity_matrix:
        s = ''
        for val in row:
            s += '%5s' % round(val, 2)
        print s

    total_average = total_sum / (len(keywords) * len(keywords))
    print 'average value in the matrix: %s' % total_average

    return keyword_similarity_matrix