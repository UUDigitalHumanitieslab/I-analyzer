#!/usr/bin/env python3

import logging
from elasticsearch import Elasticsearch
import os
from datetime import datetime
from progress.bar import Bar

es = Elasticsearch()
updated_docs = 0
bar = None

BASE_DIR = '/its/times/TDA_GDA/TDA_GDA_1785-2009/1785'
LOG_LOCATION = '/home/jvboheemen/convert_scripts'

# BASE_DIR = '/Users/3248526/corpora/times/TDA_GDA/TDA_GDA_1785-2009'
# LOG_LOCATION = '/Users/3248526/Documents'


class ProgressBar(Bar):
    message = 'Updating index'
    suffix = '%(percent).1f%% - %(eta)ds'


def add_images(page_size):
    index = 'times'
    doc_type = 'block'
    corpus_dir = BASE_DIR
    scroll = '3m'

    # Collect initial page
    page = init_search(index, doc_type, page_size, scroll)
    total_hits = page['hits']['total']
    scroll_size = len(page['hits']['hits'])

    logging.warning("Starting collection of images for {} documents in index '{}'".format(
        total_hits, index))

    while scroll_size > 0:
        # Get the current scroll ID
        sid = page['_scroll_id']
        # Process current batch of hits
        process_hits(page['hits']['hits'], index, doc_type, corpus_dir)
        # Scroll to next page
        page = es.scroll(scroll_id=sid, scroll=scroll)
        # Get the number of results in current page to control loop
        scroll_size = len(page['hits']['hits'])

    global updated_docs
    logging.warning("Updated {} documents".format(updated_docs))


def init_search(index, doc_type, page_size, scroll_timeout):
    return es.search(
        index=index,
        body={"_source": ["date", "page"]},
        doc_type=doc_type,
        params={"scroll": scroll_timeout, "size": page_size}
    )


def process_hits(hits, index, doc_type, corpus_dir):
    for doc in hits:
        date, page = doc['_source']['date'], doc['_source']['page']
        es_doc_id = doc['_id']
        image_path = compose_image_path(date, page, corpus_dir)
        if image_path:
            update_document(index, doc_type, es_doc_id, image_path)
        global bar
        bar.next()


def compose_image_path(date_string, page, corpus_dir):
    date_obj = datetime.strptime(date_string, '%Y-%m-%d')
    year, month, day = str(date_obj.year), '{0:02d}'.format(
        date_obj.month), "{0:02d}".format(date_obj.day)
    page_str = '{0:04d}'.format(int(page))
    file_name = '0FFO-{}-{}{}-{}'.format(year, month, day, page_str)+'.png'
    relative_path = os.path.join(year, year+month+day, file_name)
    complete_path = os.path.join(corpus_dir, relative_path)
    if os.path.isfile(complete_path):
        return os.path.join('TDA_GDA', 'TDA_GDA_1785-2009', relative_path)
    else:
        logging.warning('Image {} does not exist'.format(complete_path))
        return None


def update_document(index, doc_type, doc_id, image_path):
    body = {"doc": {"image_path": image_path}}
    es.update(index=index, doc_type=doc_type, id=doc_id, body=body)
    global updated_docs
    updated_docs += 1


if __name__ == "__main__":
    nr_of_docs = es.count(index=['times'])['count']
    # global bar
    bar = ProgressBar(max=nr_of_docs)

    logfile = 'indexupdate.log'
    logging.basicConfig(filename=os.path.join(LOG_LOCATION, 'indexupdate.log'),
                        format='%(asctime)s\t%(levelname)s:\t%(message)s', datefmt='%c', level=logging.WARNING)

    add_images(100)
    bar.finish()
    logging.warning(
        'Done adding scans to ES index. {} documents.'.format(nr_of_docs))
