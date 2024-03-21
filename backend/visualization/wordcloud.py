from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer

from addcorpus.models import Corpus
from addcorpus.es_settings import get_nltk_stopwords
from es import download as download

def field_stopwords(corpus_name, field_name):
    corpus = Corpus.objects.get(name=corpus_name)
    field = corpus.configuration.fields.get(name=field_name)
    if field.language and field.language is not 'dynamic':
        return get_nltk_stopwords(field.language)
    else:
        return []

def make_wordcloud_data(documents, field, corpus):
    texts = []
    for document in documents:
        content = document['_source'][field]
        if content and content != '':
            texts.append(content)

    stopwords = field_stopwords(corpus, field)
    cv = CountVectorizer(max_features=100, max_df=0.7, token_pattern=r'(?u)\b[^0-9\s]{3,30}\b', stop_words=stopwords)
    cvtexts = cv.fit_transform(texts)
    counts = cvtexts.sum(axis=0).A1
    words = list(cv.get_feature_names_out())
    freq_distribution = Counter(dict(zip(words, counts)))
    output = [{'key': word, 'doc_count': int(freq_distribution[word])} for word in words]
    return output

