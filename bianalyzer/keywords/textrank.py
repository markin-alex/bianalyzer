# -*- coding: utf-8 -*-

from bisect import bisect_left
import operator
import networkx
import re
from nltk.stem import wordnet, PorterStemmer

from .frequency import get_word_frequencies
from ..helpers import check_text_collection

default_pos_list = ['NN', 'NNP', 'NNS']
artificial_stop_words = ['using', 'furthermore', 'show', 'present', 'use', 'paper', 'multiple']


# apply syntactic filters based on POS tags
def filter_for_tags(tagged, pos_list):
    return [item for item in tagged if item[1] in pos_list and (re.match('^[a-zA-Z\'-]{4,}$', item[0]) is not None)]


def does_tag_fit(tag, pos_list):
    return tag[1] in pos_list


def normalize(tagged):
    return [item[0].replace('.', '') for item in tagged]


wordnet_lemmatizer = wordnet.WordNetLemmatizer()
porter_stemmer = PorterStemmer()


def lemmatize(word):  # TODO: consider using POS for lemmatization
    word = word.lower()
    pos = 'n'  # initially we assume that given word is a noun
    return wordnet_lemmatizer.lemmatize(word, pos=pos)


def stem_phrase(phrase):
    words = phrase.split(' ')
    stemmed_words = [porter_stemmer.stem(word) for word in words]
    return ' '.join(stemmed_words)


def filter_by_frequency(texts, keywords, min_freq=0.2, max_freq=15.0):
    word_frequencies = get_word_frequencies(texts)
    collection_len = float(len(texts))
    resulting_keywords = []
    odd_keywords = []
    for keyword in keywords:
        freq = (word_frequencies.get(keyword, 0.0) / collection_len) * 100.0
        if min_freq <= freq <= max_freq:
            resulting_keywords.append((keyword, freq))
        else:
            odd_keywords.append((keyword, freq))

    # print 'filtered over frequency keywords: %s' % ', '.join(item[0] for item in odd_keywords)
    keywords = [k[0] for k in resulting_keywords]
    return keywords


def filter_by_stemming(keywords):
    stems = {}
    for kw in keywords:
        kw_stem = porter_stemmer.stem(kw)
        if kw_stem in stems:
            if len(kw) < len(stems[kw_stem]):
                stems[kw_stem] = kw
        else:
            stems[kw_stem] = kw
    return stems.keys(), stems.values()


def join_keywords(text_list, page_rank, keywords, concatenation_occurrences):
    sorted_keywords = sorted(keywords)

    keyphrases = {}
    marked = {}
    for i in range(len(text_list)):
        tokens = text_list[i]
        tokens = [token[0] for token in tokens]
        is_last_keyword = False
        strike_len = 0
        cumulative_rank = 0.0
        for j in range(len(tokens) + 1):
            if j < len(tokens):
                ind = bisect_left(sorted_keywords, tokens[j])
            else:
                ind = len(sorted_keywords)
            is_current_keyword = (ind < len(sorted_keywords) and sorted_keywords[ind] == tokens[j])

            if is_last_keyword and (not is_current_keyword) and strike_len > 1:
                keyphrase = ' '.join(tokens[j - strike_len:j])
                # if strike_len > 2:
                #     print keyphrase
                rank = cumulative_rank / float(strike_len)
                if keyphrases.get(keyphrase) is None:
                    keyphrases[keyphrase] = (set(), rank)

                keyphrases[keyphrase][0].add(i)
                if len(keyphrases[keyphrase][0]) > concatenation_occurrences:
                    for token in tokens[j - strike_len:j]:
                        marked[token] = True

            if is_current_keyword:
                strike_len += 1
                cumulative_rank += page_rank[tokens[j]]
                is_last_keyword = True
            else:
                strike_len = 0
                cumulative_rank = 0.0
                is_last_keyword = False

    final_keywords = []
    for keyphrase in keyphrases:
        if len(keyphrases[keyphrase][0]) > concatenation_occurrences:
            final_keywords.append((keyphrase, keyphrases[keyphrase][1]))
    for keyword in keywords:
        if not marked.get(keyword, False):
            final_keywords.append((keyword, page_rank[keyword]))

    final_keywords = sorted(final_keywords, key=operator.itemgetter(1), reverse=True)
    final_keywords = [keyword[0] for keyword in final_keywords]
    return final_keywords


def extract_keywords_via_textrank(texts, window_size=5, keyword_limit=150, frequency_filter=True, min_freq=0.2,
                                  max_freq=15.0, stemming_filter=True, concatenate=True,  concatenation_occurrences=2,
                                  lemmatize_words=True, pos_list=default_pos_list):
    check_text_collection(texts)
    word_set = set()
    # stemmed_words = {}
    text_list = []
    raw_texts = []
    for text in texts:
        tagged_tokens = text.tagged_tokens
        if tagged_tokens is None:
            tagged_tokens = text.tag_tokens()

        if lemmatize_words:
            tagged_tokens = [(lemmatize(word), pos) for (word, pos) in tagged_tokens]
        word_list = [x for x in tagged_tokens]

        tagged_tokens = filter_for_tags(tagged_tokens, pos_list)
        tagged_tokens = normalize(tagged_tokens)

        raw_words = [x for x in tagged_tokens]
        raw_texts.append(raw_words)

        text_list.append(word_list)

        for token in tagged_tokens:
            word_set.add(token)

    # print "words in set: %s" % len(word_set)
    word_graph = networkx.Graph()
    word_set_list = list(word_set)
    word_graph.add_nodes_from(word_set_list)

    for i, text in enumerate(texts):
        window_start = 0
        tokens = text_list[i]
        while window_start < len(tokens):
            window = filter_for_tags(tokens[window_start:window_start + window_size + 1], pos_list)
            if len(window) > 0 and does_tag_fit(window[0], pos_list):
                node1 = window[0][0]
                for j in range(1, len(window)):
                    node2 = window[j][0]
                    word_graph.add_edge(node1, node2)

            window_start += 1

    # pageRank - initial value of 1.0, error tolerance of 0,0001,
    calculated_page_rank = networkx.pagerank(word_graph)

    # most important words in ascending order of importance
    keywords = sorted(calculated_page_rank, key=calculated_page_rank.get, reverse=True)

    keywords_with_tr = []
    max_tr = calculated_page_rank[keywords[0]]
    for keyword in keywords:
        keywords_with_tr.append((keyword, (calculated_page_rank[keyword] / max_tr) * 100.0))
    # for i, (keyword, rank) in enumerate(keywords_with_tr):
    #     print '%s. %s\t%s' % ((i + 1), keyword, rank)

    # limit the number of keywords for further processing
    keywords = keywords[0:keyword_limit]

    for stop_word in artificial_stop_words:
        if stop_word in keywords:
            keywords.remove(stop_word)

    if stemming_filter:
        stems, keywords = filter_by_stemming(keywords)

    if frequency_filter:
        keywords = filter_by_frequency(raw_texts, keywords, min_freq, max_freq)

    if not concatenate:
        return keywords

    final_keywords = join_keywords(text_list, calculated_page_rank, keywords, concatenation_occurrences)
    print 'extracted keyphrases: %s' % ', '.join(item for item in final_keywords)

    return final_keywords


def write_keywords_to_file(path, keywords):
    output_file = open(path, 'w+')
    for keyword in keywords:
        output_file.write(keyword + '\n')

    output_file.close()
