from addcorpus.json_corpora.import_json import import_json_corpus

def test_import(db, json_corpus_data):
    corpus = import_json_corpus(json_corpus_data)

    assert corpus.name == 'example'
    assert corpus.has_configuration
