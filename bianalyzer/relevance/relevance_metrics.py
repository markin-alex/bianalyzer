# -*- coding: utf-8 -*-
from math import log

from ..texts import porter_stemmer


def tf_idf(collection_length, collection_occurrences, article_statistics, keyword):
    # Let's assume that stemming is done by default
    keyword = keyword.lower()
    if collection_occurrences == 0:
        return 0

    word_freq = keyword_frequency(article_statistics, keyword)
    text_length = article_statistics.text_length
    if text_length == 0:
        return 0

    tf = float(word_freq) / float(text_length)
    idf = calculate_idf(collection_length, collection_occurrences)
    tfidf = tf * idf
    return tfidf


def bm25(collection_length, collection_occurrences, average_document_length, article_statistics, keyword,
         k1=1.5, b=0.75):
    keyword = keyword.lower()
    if collection_occurrences == 0:
        return 0
    word_freq = float(keyword_frequency(article_statistics, keyword))
    text_length = float(article_statistics.text_length)
    idf = calculate_idf(collection_length, collection_occurrences)
    bm25_score = idf * ((k1 + 1.0) * word_freq) / (k1 * (1 - b + b * text_length / average_document_length) + word_freq)
    return bm25_score


def ast_metric(collection, article, keyword):
    pass


def calculate_idf(total_articles, articles_with_keyword_num):
    if articles_with_keyword_num == 0:
        return 0

    idf = log(float(total_articles) / articles_with_keyword_num, 2)
    return idf


def keyword_frequency(article_statistics, keyword, stemmed=True):
    keyword = keyword.lower()
    keyphrase_tokens = keyword.split(' ')
    keyphrase_tokens = [token for token in keyphrase_tokens if len(token) > 0]
    if len(keyphrase_tokens) >= 3:
        return keyphrase_set_frequency(article_statistics, keyphrase_tokens, stemmed)
    if len(keyphrase_tokens) <= 1:
        return single_keyword_frequency(article_statistics, keyword, stemmed)
    else:
        return keyphrase_frequency(article_statistics, keyphrase_tokens, stemmed)


def single_keyword_frequency(article_statistics, keyword, stemmed):
    if stemmed:
        keyword = porter_stemmer.stem(keyword)
    word_dict = article_statistics.stemmed_word_dict if stemmed else article_statistics.word_dict
    return len(word_dict.get(keyword, []))


def keyphrase_frequency(article_statistics, keyphrase_tokens, stemmed):
    first_word = keyphrase_tokens[0]
    second_word = keyphrase_tokens[1]
    if stemmed:
        first_word = porter_stemmer.stem(first_word)
        second_word = porter_stemmer.stem(second_word)
    word_dict = article_statistics.stemmed_word_dict if stemmed else article_statistics.word_dict
    first_occurrences = word_dict.get(first_word, [])
    second_occurrences = word_dict.get(second_word, [])
    if len(first_occurrences) <= 0 or len(second_occurrences) <= 0:
        return 0

    cooccurrences = 0
    first_current = 0
    second_current = 0
    while first_current < len(first_occurrences) and second_current < len(second_occurrences):
        if abs(first_occurrences[first_current] - second_occurrences[second_current]) <= 1:
            cooccurrences += 1
        if first_occurrences[first_current] > second_occurrences[second_current]:
            second_current += 1
        else:
            first_current += 1
    if first_current == len(first_occurrences) and second_current < len(second_occurrences) - 1:
        if abs(first_occurrences[first_current - 1] - second_occurrences[second_current + 1]) <= 1:
            cooccurrences += 1
    if second_current == len(second_occurrences) and first_current < len(first_occurrences) - 1:
        if abs(second_occurrences[second_current - 1] - first_occurrences[first_current + 1]) <= 1:
            cooccurrences += 1

    return cooccurrences


def keyphrase_set_frequency(article_statistics, keyphrase_tokens, stemmed):
    words = keyphrase_tokens
    if stemmed:
        words = [porter_stemmer.stem(word) for word in words]
    word_dict = article_statistics.stemmed_word_dict if stemmed else article_statistics.word_dict
    word_occurrences = set()
    all_word_occurrences = []
    for word in words:
        occurrences = set(word_dict.get(word, []))
        all_word_occurrences.append(occurrences)
        word_occurrences.update(occurrences)

    word_occurrences = sorted(word_occurrences)

    cooccurrences = 0
    strike_len = 1
    i = 1
    while i < len(word_occurrences):
        if word_occurrences[i] == word_occurrences[i - 1] + 1:
            strike_len += 1
        else:
            strike_len = 1

        if strike_len == len(words):
            fits = True
            for j, word in enumerate(words):
                ind = word_occurrences[i] - len(words) + j + 1
                fits = fits and (ind in all_word_occurrences[j])
            if fits:
                cooccurrences += 1
            strike_len = 1
            i += 1

        i += 1

    return cooccurrences
