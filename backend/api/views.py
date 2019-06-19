'''
Present the data to the user through a web interface.
'''
import json
import base64
import logging
import math
import functools
import logging
logging.basicConfig(format='%(message)s')
from os.path import dirname, split, join, isfile, getsize
import sys
import tempfile
from io import BytesIO
from PyPDF2 import PdfFileReader, PdfFileWriter
from datetime import datetime, timedelta
from celery import chain
from werkzeug.security import generate_password_hash
from flask import Flask, Blueprint, Response, request, abort, current_app, \
    render_template, url_for, jsonify, redirect, flash, send_file, stream_with_context, send_from_directory, session, make_response
import flask_admin as admin
from flask_login import LoginManager, login_required, login_user, \
    logout_user, current_user
from flask_mail import Message

from ianalyzer import models, celery_app
from es import download
from addcorpus.load_corpus import load_all_corpora, load_corpus

from api.user_mail import send_user_mail
from . import security
from . import analyze
from . import tasks
from . import api

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(message)s')


@api.route('/ensure_csrf', methods=['GET'])
def ensure_csrf():
    return jsonify({'success': True})


# endpoint for registration new user via signup form
@api.route('/register', methods=['POST'])
def api_register():
    if not request.json:
        abort(400)

    # Validate user's input
    username = request.json['username']
    email = request.json['email']
    is_valid_username = security.is_unique_username(username)
    is_valid_email = security.is_unique_non_solis_email(email)
        
    if not is_valid_username or not is_valid_email:
        return jsonify({
            'success': False,
            'is_valid_username': is_valid_username,
            'is_valid_email': is_valid_email
        })
    token = security.get_token(username)
    # try sending the email
    if not send_user_mail(
        email,
        username,
        "Thank you for signing up at I-analyzer",
        "User registration",
        "Thank you for creating an I-analyzer account.",
        "Please click the link below to confirm " + \
        "your email address and finish your registration.",
        current_app.config['BASE_URL']+'/api/registration_confirmation/'+token,
        "Confirm registration",
        True
    ):
        return jsonify({
            'success': False,
            'is_valid_username': True,
            'is_valid_email': True
        })

    # if email was succesfully sent, add user to db
    add_basic_user(username, request.json['password'], email, False)

    return jsonify({'success': True})    

# endpoint for the confirmation of user if link in email is clicked.
@api.route('/registration_confirmation/<token>', methods=['GET'])
def api_register_confirmation(token):

    expiration = 60*60*72  # method does not return email after this limit
    username = security.get_original_token_input(token, expiration)
    
    if not username:
        flash('The confirmation link is invalid or has expired.', 'danger')

    user = models.User.query.filter_by(username=username).first_or_404()
    user.active = True
    models.db.session.add(user)
    models.db.session.commit()

    return redirect(current_app.config['BASE_URL']+'/login?isActivated=true')

@api.route('/request_reset', methods=['POST'])
def api_request_reset():
    if not request.json:
        abort(400)
    email = request.json['email']
    users = models.User.query.filter_by(email=email).all()
    message = 'No registered user for this e-mail address.'
    if not users:
        return jsonify({
            'success': False,
            'message': message
        })
    user = next((user for user in users if user.saml==False), None)
    if not user:
        return jsonify({
            'success': False,
            'message': message + " Log in via your Solis-ID or make a new account."})
    token = security.get_token(user.username)
    if not send_user_mail(
        email, 
        user.username,
        "Your password can be reset",
        "Password reset",
        "You requested a password reset.",
        "Please click the link below to enter " + \
        "and confirm your new password.",
        current_app.config['BASE_URL']+'/reset-password/'+token,
        "Reset password"
        ):
        return jsonify({'success': False, 'message': 'Email could not be sent.'})
    return jsonify({'success': True, 'message': 'An email was sent to your address.'})


@api.route('/reset_password', methods=['POST'])
def api_reset_password():
    if not request.json or not all(x in request.json for x in ['password', 'token']):
        return jsonify({'success': False, 'message': 'Errors during request'})
    expiration = 60*60*72  # method does not return email after this limit
    username = security.get_original_token_input(request.json['token'], expiration)
    if not username:
        return jsonify({'success': False, 'message': 'Your token is not valid or has expired.'})
    user = models.User.query.filter_by(username=username).first_or_404()
    if not user:
        return jsonify({'success': False, 'message': 'User doesn\'t exist.'})
    security.login_user(user) 
    password = request.json['password']
    user.password = generate_password_hash(password)
    models.db.session.commit()
    return jsonify({'success': True, 'username': username})


@api.route('/es_config', methods=['GET'])
@login_required
def api_es_config():
    return jsonify([{
        'name': server_name,
        'host': url_for('es.forward_head', server_name=server_name, _external=True),
        'port': None,
        'chunkSize': server_config['chunk_size'],
        'maxChunkBytes': server_config['max_chunk_bytes'],
        'bulkTimeout': server_config['bulk_timeout'],
        'overviewQuerySize': server_config['overview_query_size'],
        'scrollTimeout': server_config['scroll_timeout'],
        'scrollPagesize': server_config['scroll_page_size']
    } for server_name, server_config in current_app.config['SERVERS'].items()])


@api.route('/corpus', methods=['GET'])
@login_required
def api_corpus_list():
    load_all_corpora()
    response = jsonify(dict(
        (key, dict(
            server_name=current_app.config['CORPUS_SERVER_NAMES'][key],
            **current_app.config['CORPUS_DEFINITIONS'][key].serialize()
        )) for key in
        current_app.config['CORPUS_DEFINITIONS'].keys()
    ))
    return response


@api.route('/corpusimage/<corpus>/<image_name>', methods=['GET'])
@login_required
def api_corpus_image(corpus, image_name):
    '''
    Return the image for a corpus.
    '''
    return send_from_directory(join(
        dirname(current_app.config['CORPORA'][corpus]), 
        current_app.config['IMAGE_PATH']), '{}'.format(image_name))

@api.route('/corpusdescription/<corpus>/<description_name>', methods=['GET'])
@login_required
def api_corpus_description(corpus, description_name):
    '''
    Return comprehensive information on the corpus.
    '''
    corpus_dir = dirname(current_app.config['CORPORA'][corpus])
    return send_from_directory(corpus_dir, 'description/{}'.format(description_name))


@api.route('/corpusdocument/<corpus>/<document_name>', methods=['GET'])
@login_required
def api_corpus_document(corpus, document_name):
    '''
    Return a document for a corpus.
    '''
    corpus_dir = dirname(current_app.config['CORPORA'][corpus])
    return send_from_directory(corpus_dir, 'documents/{}'.format(document_name))


@api.route('/download', methods=['POST'])
@login_required
def api_download():
    error_response = make_response("", 400)
    error_response.headers['message'] = "Download failed: "
    if not request.json:
        error_response.headers.message += 'missing request body.'
        return error_response
    elif request.mimetype != 'application/json':
        error_response.headers.message += 'unsupported mime type.'
        return error_response
    elif not all(key in request.json.keys() for key in ['es_query', 'corpus', 'fields']):
        error_response.headers['message'] += 'missing arguments.'
        return error_response
    elif request.json['size']>1000:
        error_response.headers['message'] += 'too many documents requested.'
        return error_response
    else:
        search_results = download.normal_search(request.json['corpus'], request.json['es_query'], request.json['size'])
        filepath = tasks.make_csv.delay(search_results, request.json, current_user.username)
        csv_file = filepath.get()
        response = make_response(send_file(csv_file, mimetype='text/csv'))
        response.headers['filename'] = split(csv_file)[1]
        return response


# endpoint for backend handling of large csv files
@api.route('/download_task', methods=['POST'])
@login_required
def api_download_task():
    error_response = make_response("", 400)
    error_response.headers['message'] = "Download failed: "
    if not request.json:
        error_response.headers.message += 'missing request body.'
        return error_response
    elif request.mimetype != 'application/json':
        error_response.headers.message += 'unsupported mime type.'
        return error_response
    elif not all(key in request.json.keys() for key in ['es_query', 'corpus', 'fields']):
        error_response.headers['message'] += 'missing arguments.'
        return error_response
    elif not current_user.email:
        error_response.headers['message'] += 'user email not known.'
        return error_response
    # Celery task
    csv_task = chain(tasks.download_scroll.s(request.json, current_user.download_limit), 
        tasks.make_csv.s(request.json, current_user.username, current_user.email))
    csvs = csv_task.apply_async()
    if not csvs:
        return jsonify({'success': False, 'message': 'Could not create csvs.'})
    else:
        return jsonify({'success': True, 'task_ids': [csvs.id, csvs.parent.id]})

    

# endpoint for link send in email to download csv file
@api.route('/csv/<filename>', methods=['get'])
def api_csv(filename):
    return send_from_directory( current_app.instance_path, '{}'.format(filename))


@api.route('/login', methods=['POST'])
def api_login():
    if not request.json:
        abort(400)
    username = request.json['username']
    password = request.json['password']
    user = security.validate_user(username, password)

    if user is None:
        response = jsonify({'success': False})
    else:
        security.login_user(user)
        response = create_success_response(user)

    return response


def add_basic_user(username, password, email, is_active):
    ''' Add a user with the role 'basic' to the database '''

    basic_role = models.Role.query.filter_by(name='basic').first()
    pw_hash = None
    if (password):
        pw_hash = generate_password_hash(password)    
    new_user = models.User(
        username=username,
        email=email,
        active=is_active,
        password=pw_hash,
        role_id=basic_role.id,
    )
    models.db.session.add(new_user)
    models.db.session.commit()
    return new_user


def create_success_response(user):
    corpora = [{
        'name': corpus.name,
        'description': corpus.description
    } for corpus in user.role.corpora]
    role = {
        'name': user.role.name, 
        'description': user.role.description, 
        'corpora': corpora
    }    
    response = jsonify({
        'success': True,
        'id': user.id,
        'username': user.username,
        'role': role,
        'downloadLimit': user.download_limit
    })

    return response

@api.route('/log', methods=['POST'])
@login_required
def api_log():
    if not request.json:
        abort(400)
    msg_type = request.json['type']
    msg = request.json['msg']

    if msg_type == 'info':
        logger.info(msg)
    else:
        logger.error(msg)

    return jsonify({'success': True})


@api.route('/logout', methods=['POST'])
def api_logout():
    if current_user.is_authenticated:
        logout_user()
    return jsonify({'success': True})


@api.route('/check_session', methods=['POST'])
def api_check_session():
    """
    Check that the specified user is still logged on.
    """
    if not request.json:
        abort(400)
    username = request.json['username']

    if not current_user.is_authenticated or current_user.username != username:
        abort(401)
    else:
        return jsonify({'success': True})


@api.route('/query', methods=['PUT'])
@login_required
def api_query():
    if not request.json:
        abort(400)

    query_json = request.json['query']
    if 'filters' in query_json:
        query_model = json.loads(query_json)
        for search_filter in query_model['filters']:
            # no need to save defaults in database
            del search_filter['defaultData']
            if 'options' in search_filter['currentData']:
                # options can be lengthy, just save user settings
                del search_filter['currentData']['options']
        query_json = json.dumps(query_model)
    corpus_name = request.json['corpus_name']

    if 'id' in request.json:
        query = models.Query.query.filter_by(id=request.json['id']).first()
    else:
        query = models.Query(
            query=query_json, corpus_name=corpus_name, user=current_user)

    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    query.started = datetime.now() if ('markStarted' in request.json and request.json['markStarted'] == True) \
        else (datetime.strptime(request.json['started'], date_format) if 'started' in request.json else None)
    query.completed = datetime.now() if ('markCompleted' in request.json and request.json['markCompleted'] == True)  \
        else (datetime.strptime(request.json['completed'], date_format) if 'completed' in request.json else None)

    query.aborted = request.json['aborted']
    query.transferred = request.json['transferred']

    models.db.session.add(query)
    models.db.session.commit()

    return jsonify({
        'id': query.id,
        'query': query.query_json,
        'corpus_name': query.corpus_name,
        'started': query.started,
        'completed': query.completed,
        'aborted': query.aborted,
        'transferred': query.transferred,
        'userID': query.userID
    })


@api.route('/search_history', methods=['GET'])
@login_required
def api_search_history():
    user = current_user
    queries = user.queries
    return jsonify({
        'queries': [{
            'query': query.query_json,
            'corpusName': query.corpus_name,
            'started': query.started,
            'completed': query.completed,
            'transferred': query.transferred
        } for query in queries]
    })


@api.route('/wordcloud', methods=['POST'])
@login_required
def api_wordcloud():
    ''' get the results for a small batch of results right away '''
    if not request.json:
        abort(400)
    if request.json['size']>1000:
        abort(400)
    else:
        list_of_texts = download.normal_search(request.json['corpus'], request.json['es_query'], request.json['size'])
        word_counts = tasks.make_wordcloud_data.delay(list_of_texts, request.json)
        if not word_counts:
            return jsonify({'success': False, 'message': 'Could not generate word cloud data.'})
        else:
            return jsonify({'success': True, 'data': word_counts.get()})


@api.route('/wordcloud_tasks', methods=['POST'])
@login_required
def api_wordcloud_tasks():
    ''' schedule a celery task and return the task id '''
    if not request.json:
        abort(400)
    else:
        word_counts_task = chain(tasks.get_wordcloud_data.s(request.json), tasks.make_wordcloud_data.s(request.json))
        word_counts = word_counts_task.apply_async()
        if not word_counts:
            return jsonify({'success': False, 'message': 'Could not set up word cloud generation.'})
        else:
            return jsonify({'success': True, 'task_ids': [word_counts.id, word_counts.parent.id]})


@api.route('/task_outcome/<task_id>', methods=['GET'])
@login_required
def api_task_outcome(task_id):
    results = celery_app.AsyncResult(id=task_id)
    if not results:
        return jsonify({'success': False, 'message': 'Could not get word cloud data.'})
    else:        
        return jsonify({'success': True, 'results': results.get()})


@api.route('/abort_tasks', methods=['POST'])
@login_required
def api_abort_tasks():
    if not request.json:
        abort(400)
    else:
        task_ids = request.json['task_ids']
        try:
            celery_app.control.revoke(task_ids, terminate=True)
        except Exception as e:
            logger.critical(e)
            return jsonify({'success': False})
        return jsonify({'success': True})


@api.route('/get_scan_image/<corpus_index>/<path:image_path>', methods=['GET'])
@login_required
def api_get_scan_image(corpus_index, image_path):
    backend_corpus = load_corpus(corpus_index)

    if corpus_index in [corpus.name for corpus in current_user.role.corpora]:
        absolute_path = join(backend_corpus.data_directory, image_path)
        if not isfile(absolute_path):
            abort(404)
        else:
            return send_file(absolute_path, mimetype='image/png')

@api.route('/source_pdf', methods=['POST'])
@login_required
def api_get_pdf():
    if not request.json:
        abort(400)

    corpus_index = request.json['corpus_index']
    backend_corpus = load_corpus(corpus_index)

    if not corpus_index in [corpus.name for corpus in current_user.role.corpora]:
        abort(400)
    else:
        pages_returned = 5 #number of pages that is displayed. must be odd number.
        
        home_page = request.json['page'] #the page corresponding to the document
        image_path = request.json['image_path']
        absolute_path = join(backend_corpus.data_directory, image_path)

        if not isfile(absolute_path):
            abort(404)

        input_pdf, pdf_info = retrieve_pdf(absolute_path)
        pages, home_page_index = pdf_pages(pdf_info['all_pages'], pages_returned, home_page)
        out = build_partial_pdf(pages, input_pdf)
        
        response = make_response(send_file(out, mimetype='application/pdf', attachment_filename="scan.pdf", as_attachment=True))
        pdf_header = json.dumps({
            "pageNumbers": [p+1 for p in pages], #change from 0-indexed to real page
            "homePageIndex": home_page_index+1, #change from 0-indexed to real page
            "fileName": pdf_info['filename'],
            "fileSize": pdf_info['filesize']
        })
        response.headers['pdfinfo'] = pdf_header
    return response

@api.route('/download_pdf/<corpus_index>/<path:filepath>', methods=['GET'])
@login_required 
def api_download_pdf(corpus_index, filepath):
    backend_corpus = load_corpus(corpus_index)

    if corpus_index in [c.name for c in current_user.role.corpora]:
        absolute_path = join(backend_corpus.data_directory, filepath)
        return send_file(absolute_path, as_attachment=True)


@api.route('/get_related_words', methods=['POST'])
@login_required
def api_get_related_words():
    if not request.json:
        abort(400)
    results = analyze.get_diachronic_contexts(
        request.json['query_term'],
        request.json['corpus_name']
    )
    if isinstance(results, str):
        # the method returned an error string
        response = jsonify({
            'success': False,
            'message': results})
    else:
        response = jsonify({
            'success': True,
            'related_word_data': {
                'similar_words_all': results[0],
                'similar_words_subsets': results[1],
                'time_points': results[2]
            }
        }) 
    return response


@api.route('/get_related_words_time_interval', methods=['POST'])
@login_required
def api_get_related_words_time_interval():
    if not request.json:
        abort(400)
    results = analyze.get_context_time_interval(
        request.json['query_term'],
        request.json['corpus_name'],
        request.json['time']
    )
    if isinstance(results, str):
        # the method returned an error string
        response = jsonify({
            'success': False,
            'message': results})
    else:
        response = jsonify({
            'success': True,
            'related_word_data': {
                'similar_words_subsets': results,
                'time_points': [request.json['time']]
            }
        }) 
    return response

def pdf_pages(all_pages, pages_returned, home_page):
    '''
    Decide which pages should be returned, and the index of the home page in the resulting list
    '''
    context_radius = int((pages_returned - 1) / 2) #the number of pages before and after the initial
    #the page is within context_radius of the beginning of the pdf:
    if (home_page - context_radius) <= 0:
        pages = all_pages[:home_page+context_radius+1]
        home_page_index = pages.index(home_page)

    #the page is within context_radius of the end of the pdf:
    elif (home_page + context_radius) >= len(all_pages):
        pages = all_pages[home_page-context_radius:]
        home_page_index = pages.index(home_page)

    #normal case:
    else:
        pages = all_pages[(home_page-context_radius):(home_page+context_radius+1)]
        home_page_index = context_radius
    
    return pages, home_page_index

def build_partial_pdf(pages, input_pdf):
    '''
    Build a partial pdf consisting of the requires pages.
    Returns a temporary file stream.
    '''
    tmp = BytesIO()
    pdf_writer = PdfFileWriter()
    for p in pages:
        pdf_writer.addPage(input_pdf.getPage(p))
    pdf_writer.write(tmp)
    tmp.seek(0) #reset stream

    return tmp

def retrieve_pdf(path):
    '''
    Retrieve the pdf as a file object, and gather some additional information.
    '''
    pdf = PdfFileReader(path, 'rb')
    title = pdf.getDocumentInfo().title
    _dir, filename = split(path)
    num_pages = pdf.getNumPages()

    info = {
        'filename': title if title else filename,
        'filesize': sizeof_fmt(getsize(path)),
        'all_pages': list(range(0, num_pages))
     }

    return pdf, info

def sizeof_fmt(num, suffix='B'):
    '''
    Converts numerical filesize to human-readable string.
    Maximum of three numbers before the decimal, and one behind.
    E.g. 124857000 -> "119.1 MB"
    '''
    for unit in ['','K','M','G']:
        if abs(num) < 1024.0:
            return "{:3.1f} {}{}".format(num, unit, suffix)
        num /= 1024.0
