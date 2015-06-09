# Bianalyzer

## Description

**Bianalyzer** provides methods for bicluster analysis over unstructured text data.

It is primarily designed to

1. find overlapping biclusters of texts and keyphrases via processing keyphrase/texts relevance matrix;
2. find thematic biclusters of keyphrases based on the co-occurrence data.

**Bianalyzer** package also allows to download collections of abstracts from such Digital Libraries as IEEE Xplore and Springer.
Besides, it provides functionality to derive keyphrases from the text collections using the popular TextRank method.
In case you want to work with the DigitalLibrary-provided keyphrases, you can download them as well (only for IEEE Xplore abstracts).
These includes keyphrases from the Inspec database and author keywords that were listed in the article itself.


## How to use *Bianalyzer*

Here is a typical scenario of work with the **Bianalyzer** library:

1. Download a collection of abstracts from a Digital Library (either IEEE Xplore or Springer)
2. Extract a set of keyphrases from the obtained collection via TextRank algorithm
3. Build a keyphrase-to-text relevance matrix one of the following metrics:

    * TF-IDF metric;
    * Okapi BM25 metric;
    * Annotated Suffix Tree based metric;
    * Raw frequency metric (it simply calculates the number of times a keyphrase appears in a document);
    * Normalized frequency metric (number of occurrences divided by a document length excluding stop-words).

4. Calculate a keyphrase-to-keyphrase similarity matrix given a relevance matrix and a user-defined relevance threshold
5. Find dense keyphrase biclusters in the similarity matrix
6. Draw a keyphrase graph based on the found keyphrase biclusters

One can run the use-case above using the following small Python-script:

```python
from bianalyzer.keywords import extract_keywords_via_textrank
from bianalyzer.abstracts import download_abstracts
from bianalyzer import BianalyzerText
from bianalyzer.relevance import construct_relevance_matrix, construct_similarity_matrix, RelevanceMetric
from bianalyzer.biclustering import get_keyword_biclusters, GreedyBBox

articles = download_abstracts('IEEE', 'cluster analysis', 3000)
bianalyzer_texts = [BianalyzerText(article.abstract_text) for article in articles]
keywords = extract_keywords_via_textrank(bianalyzer_texts, keyword_limit=300, concatenation_occurrences=3)
relevance_matrix = construct_relevance_matrix(keywords, bianalyzer_texts, RelevanceMetric.bm25)
similarity_matrix = construct_similarity_matrix(relevance_matrix, 0.15)
biclustering_result = get_keyword_biclusters(similarity_matrix, GreedyBBox)
edges = construct_keyword_graph(biclustering_result.biclusters, min_density=0.2)
draw_keyword_biclusters(edges)
```
