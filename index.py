#!/usr/bin/env python3

'''
Index documents from the original XML files to ElasticSearch.
'''

import logging
from pyelasticsearch import bulk_chunks
from datetime import datetime

import config
import factories
import extractor
import fields

def index(elasticsearch=None):
    es = elasticsearch or factories.elasticsearch()

    for year in (1785, 1950, 2000, 2010):
        logging.info('(!) Logging year {}'.format(year))

        files = extractor.filenames(
            start=datetime(year=year, month=1, day=1),
            end=datetime(year=year, month=12, day=31)
        )
    
        docs = extractor.dicts(fields.default, files)
        for chunk in bulk_chunks(
                map(es.index_op, docs),
                docs_per_chunk=500,
                bytes_per_chunk=20000
            ):
            es.bulk(chunk, doc_type='article', index='library{}'.format(year))



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info('Started indexing.')
    index()
    logging.info('Finished indexing.')