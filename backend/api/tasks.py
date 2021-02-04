import requests
import csv
import json
import os.path as op
from flask import Flask, abort, current_app, render_template
from flask_mail import Mail, Message
import logging
from requests.exceptions import Timeout, ConnectionError, HTTPError
import re

from api import analyze
from api.user_mail import send_user_mail
from es import es_forward, download
from ianalyzer import celery_app

logger = logging.getLogger(__name__)


@celery_app.task()
def download_scroll(request_json, download_size=10000):
    results = download.scroll(request_json['corpus'], request_json['es_query'], download_size)
    return results


@celery_app.task()
def make_csv(results, filename, request_json):
    filepath = create_csv(results, request_json['fields'], filename)
    return filepath


@celery_app.task()
def get_wordcloud_data(request_json):
    list_of_texts = download.scroll(request_json['corpus'], request_json['es_query'], current_app.config['WORDCLOUD_LIMIT'])
    return list_of_texts


@celery_app.task()
def make_wordcloud_data(list_of_texts, request_json):
    word_counts = analyze.make_wordcloud_data(list_of_texts, request_json['field'])
    return word_counts


def create_filename(route):
    """ 
    name the file given the route of the search
    cut the file name to max length of 255 (including route and extension) 
    """
    filename = re.sub(r';|%\d+', '_', re.sub(r'\$', '', route.split('/')[2]))
    max_filename_length = 251-len(current_app.config['CSV_FILES_PATH'])
    if len(filename) > max_filename_length:
        filename = filename[:max_filename_length]
    filename += '.csv'
    return filename


def create_csv(results, fields, filename):
    entries = []
    for result in results:
        entry={}
        for field in fields:
            #this assures that old indices, which have their id on
            #the top level '_id' field, will fill in id here
            if field=="id" and "_id" in result: 
                entry.update( {field: result['_id']} )
            if field in result['_source']:
                entry.update( {field:result['_source'][field]} )
        entries.append(entry)
    csv.register_dialect('myDialect', delimiter=',', quotechar='"',
                         quoting=csv.QUOTE_NONNUMERIC, skipinitialspace=True)                  
    filepath = op.join(current_app.config['CSV_FILES_PATH'], filename)
    # newline='' to prevent empty double lines
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, dialect='myDialect')
        writer.writeheader()
        for row in entries:
            writer.writerow(row)
    return filepath