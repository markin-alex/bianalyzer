# -*- coding: utf-8 -*-
import sys
import getopt

from bianalyzer import BianalyzerText
from bianalyzer.abstracts import download_abstracts
from bianalyzer.biclustering import get_keyword_biclusters, GreedyBBox, get_keyword_text_biclusters, \
    save_keyword_text_biclusters
from bianalyzer.biclustering.keywords_analysis import save_keyword_biclusters
from bianalyzer.keywords import extract_keywords_via_textrank
from bianalyzer.relevance import construct_relevance_matrix, construct_similarity_matrix

usage = "Bianalyzer should be called as:\n" \
        "bianalyzer [-s <source>] [-S <springer_api_key>] [-m <relevance_metric>] [-q <query>] [-r] [-d] biclusters " \
        "<abtracts_number> <path_to_file>"

supported_sources = ['IEEE', 'Springer']
supported_relevance_metrics = ['tf-idf', 'bm25', 'ast', 'frequency', 'normalized_frequency']


def main():

    def print_error(message):
        print message + '\n'
        print usage

    args = sys.argv[1:]

    opts, args = getopt.getopt(args, "s:S:m:q:rd")
    opts = dict(opts)
    opts.setdefault('-s', 'IEEE')
    opts.setdefault('-S', None)
    opts.setdefault('-m', 'bm25')
    opts.setdefault('-q', 'cluster analysis')
    opts.setdefault('-r', False)
    opts.setdefault('-d', False)
    if opts['-r'] == '':
        opts['-r'] = True
    if opts['-d'] == '':
        opts['-d'] = True

    # print opts, args

    if opts['-d'] and opts['-r']:
        print_error('Cannot use both options -r and -d simultaneously')
        return 1
    if opts['-s'] not in supported_sources:
        print_error('Invalid source of abstracts. It should be either IEEE or Springer')
        return 1
    if opts['-m'] not in supported_relevance_metrics:
        print_error('Invalid relevance metric. It should be tf-idf, bm25, ast, frequency or normalized_frequency')
        return 1
    if opts['-s'] == 'Springer' and opts['-S'] == '':
        print_error('Invalid Springer API key')
    if len(args) < 3:
        print_error('Invalid command format. Please use the following format: biclusters <number> <path_to_file>')
        return 1

    command = args[0]
    abstracts_number = args[1]
    path_to_file = args[2]

    parsed = True
    try:
        abstracts_number = int(abstracts_number)
    except ValueError:
        parsed = False
    if not parsed or (abstracts_number > 5000) or (abstracts_number < 1):
        print_error('Invalid number of abstracts to download. It should be in range [1, 5000]')
        return 1

    if command == 'biclusters':
        try:
            biclusters_file = open(path_to_file, 'w')
        except Exception:
            print_error('Could not create/open the file specified')
            return 1

        try:
            articles = download_abstracts(opts['-s'], opts['-q'], abstracts_number, springer_api_key=opts['-S'])
        except Exception, e:
            print_error('Error occurred while downloading: %s' % e)
            return 1

        bianalyzer_texts = [BianalyzerText(article.abstract_text) for article in articles]
        keywords = extract_keywords_via_textrank(bianalyzer_texts)
        relevance_matrix = construct_relevance_matrix(keywords, bianalyzer_texts, opts['-m'])

        if not opts['-r']:
            similarity_matrix = construct_similarity_matrix(relevance_matrix, 0.2)
            keyword_biclusters = get_keyword_biclusters(similarity_matrix, GreedyBBox)
            save_keyword_biclusters(keyword_biclusters, biclusters_file, min_density=0.1)
            if opts['-d']:
                try:
                    from bianalyzer.graphs import construct_keyword_graph, draw_keyword_biclusters
                    edges = construct_keyword_graph(keyword_biclusters.biclusters)
                    draw_keyword_biclusters(edges)
                except Exception:
                    print '-------------------------'
                    print 'Could not draw the graph! Please, install the nodebox-opengl package'
        else:
            keyword_text_biclusters = get_keyword_text_biclusters(relevance_matrix, GreedyBBox)
            save_keyword_text_biclusters(keyword_text_biclusters, biclusters_file, min_density=0.1)

        biclusters_file.close()
    else:
        print_error('Invalid command format. Please use the following format: biclusters <number> <path_to_file>')
        return 1

if __name__ == "__main__":
    main()
