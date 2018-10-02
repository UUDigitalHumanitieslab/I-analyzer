'''
Present the data to the user through a web interface.
'''
import json
import logging
logger = logging.getLogger(__name__)
import functools
from datetime import datetime, timedelta
from flask import Flask, Blueprint, Response, request, abort, current_app, \
    render_template, url_for, jsonify, redirect, flash, stream_with_context
import flask_admin as admin
from flask_login import LoginManager, login_required, login_user, \
    logout_user, current_user
from flask_mail import Mail, Message   
from flask_sqlalchemy import SQLAlchemy
from ianalyzer import config_fallback as config
from werkzeug.security import generate_password_hash, check_password_hash
import string
from random import choice
from . import config_fallback as config
from . import factories
from . import models
from . import views
from . import security
from . import streaming
from . import corpora
from . import analyze



blueprint = Blueprint('blueprint', __name__)
admin_instance = admin.Admin(
    name='IAnalyzer', index_view=views.AdminIndexView(), endpoint='admin')
admin_instance.add_view(views.CorpusView(
    corpus_name=list(config.CORPORA.keys())[0], name='Return to search',
    endpoint=config.CORPUS_SERVER_NAMES[list(config.CORPORA.keys())[0]]))
admin_instance.add_view(views.UserView(
    models.User, models.db.session, name='Users', endpoint='users'))
admin_instance.add_view(views.RoleView(
    models.Role, models.db.session, name='Roles', endpoint='roles'))
admin_instance.add_view(views.QueryView(
    models.Query, models.db.session, name='Queries', endpoint='queries'))
login_manager = LoginManager()


def corpus_required(method):
    '''
    Wrapper to make sure that a `corpus` argument is made accessible from a
    'corpus_name' argument.
    '''

    @functools.wraps(method)
    def f(corpus_name, *nargs, **kwargs):
        corpus_definition = corpora.corpus_obj
        if not corpus_definition:
            return abort(404)
        if not current_user.has_role(corpus_name):
            return abort(403)

        # TODO: Ideally, the new variables should be made available in the
        # method in flask-style, that is, thread local
        return method(
            corpus_name=corpus_name,
            corpus_definition=corpus_definition,
            *nargs, **kwargs)

    return f


def post_required(method):
    '''
    Wrapper to add relevant POSTed data to the parameters of a function.
    Also puts data in correct format. (Requires that a `corpus` parameter is
    available, so wrap with `@corpus_required` first.
    '''

    @functools.wraps(method)
    def f(corpus_name, corpus_definition, *nargs, **kwargs):
        if not request.method == 'POST':
            abort(405)

        # Collect fields selected for appearance
        fields = (
            field
            for field in corpus_definition.fields
            if ('field:' + field.name) in request.form
        )

        # Collect filters in ES format
        filters = (
            field.search_filter.elasticsearch(request.form)
            for field in corpus_definition.fields
            if field.search_filter
        )

        return method(
            corpus_name=corpus_name,
            corpus_definition=corpus_definition,
            query_string=request.form.get('query'),
            fields=list(fields),
            filters=list(f for f in filters if f is not None),
            *nargs,
            **kwargs
        )

    return f


@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(user_id)


@blueprint.route('/', methods=['GET'])
def init():
    if current_user:
        return redirect(url_for('admin.index'))
    else:
        return redirect(url_for('admin.login'))


# endpoint for register new user via login form
@blueprint.route('/api/register', methods=['POST'])
def api_register():
    if not request.json:
        abort(400)
    
    print(request.json['password'])
    #lastname opzoeken in db als controle, of email adres gebruiken als username, maar ook dan moet die uniek zijn
    #als username niet uniek is, wordt niet opgeslagen: 500 error. Moet teruggekoppeld worden, hoe?

    #generate readable/usable pw of 6 characters with some digits, to be send via email
    # characters = string.digits + string.ascii_letters + string.digits + string.digits
    # pw =  "".join(choice(characters) for x in range(6))
    token = security.generate_confirmation_token(request.json['email'])

    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    mail = Mail(app)
    msg = Message(app.config.get('MAIL_REGISTRATION_SUBJECT_LINE'), 
                    sender = app.config.get('MAIL_FROM_ADRESS'), 
                    recipients = [ request.json['email'] ])
    #msg.body = "testing"
    msg.html=render_template('mail/new_user.html', 
                firstname=request.json['firstname'], 
                lastname=request.json['lastname'], # TODO: dit wordt loginnaam, maar eerst kijken of die naam al bestaat, en in dat geval er een cijfer achterzetten
                confirmation_link= app.config.get('BASE_URL')+'/api/registration_confirmation/'+token
    )

    #https://realpython.com/handling-email-confirmation-in-flask/

    mail.send(msg) #even uitgeschakeld

    pw_hash=generate_password_hash(request.json['password'])

    new_user = models.User(
        username=request.json['lastname'], 
        email=request.json['email'],
        active=False,
        password=pw_hash,
        #roles='times' #voorlopig zo, todo een instelling (list) in config maken welke roles een nieuwe registration standaard krijgt
        # werkt niet, roles zit in (models.role), waar user id met rol is gekoppeld. Dus eerst user maken, dan de id ervan ophalen, en daarmee insert in roles
        )
    

    db = SQLAlchemy()
    db.session.add(new_user)
    db.session.commit() # zet in db


    response=jsonify({
        'success': True, 
        'firstname':request.json['firstname'], 
        'lastname':request.json['lastname'],
        'email':request.json['email'],
        })

    return response


#endpoint for the confirmation of user if link in email is clicked.
@blueprint.route('/api/registration_confirmation/<token>', methods=['GET'])
def api_register_confirmation(token):
    
    # hier redirecten naar login scherm met een boodschap die op loginscherm wordt getoond
    #https://realpython.com/handling-email-confirmation-in-flask/

    expiration=60*60*72
    try:
        email = security.confirm_token(token, expiration)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger') #werktniet, want moet via frontend 
        # hier moet een retrun komen met json naar de frontend
    
    user = models.User.query.filter_by(email=email).first_or_404()
    #print(user)
    
    if user.active:
        flash('Account already confirmed. Please login.', 'success') #idem, moet json return worden die frontend oproept
    else:
        user.active = True
        models.db.session.add(user)
        models.db.session.commit()
    # variable active meesturen, zodat loginscherm een boodschap kan geven dat activatie gelukt is
    return redirect(config.BASE_URL+'/login?isActivated=true')
    # of een http post zenden?
    #return 'test'
    # response=jsonify({
    #     'success': True,
    #     })

   # return response


@blueprint.route('/api/es_config', methods=['GET'])
@login_required
def api_es_config():
    return jsonify([{
        'name': server_name,
        'host': server_config['host'],
        'port': server_config['port'],
        'chunkSize': server_config['chunk_size'],
        'maxChunkBytes': server_config['max_chunk_bytes'],
        'bulkTimeout': server_config['bulk_timeout'],
        'overviewQuerySize': server_config['overview_query_size'],
        'scrollTimeout': server_config['scroll_timeout'],
        'scrollPagesize': server_config['scroll_page_size']
    } for server_name, server_config in config.SERVERS.items()])


@blueprint.route('/api/corpus', methods=['GET'])
@login_required
def api_corpus_list():
    response = jsonify(dict(
        (key, dict(
            server_name=config.CORPUS_SERVER_NAMES[key],
            **corpora.DEFINITIONS[key].serialize()
        )) for key in
        corpora.DEFINITIONS.keys()
    ))
    return response


@blueprint.route('/api/login', methods=['POST'])
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
        response = jsonify({
            'success': True,
            'id': user.id,
            'username': user.username,
            'roles': [{
                'name': role.name,
                'description': role.description
            } for role in user.roles],
            'downloadLimit': user.download_limit,
            'queries': [{
                'query': query.query_json,
                'corpusName': query.corpus_name
            } for query in user.queries]
        })

    return response


@blueprint.route('/api/log', methods=['POST'])
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


@blueprint.route('/api/logout', methods=['POST'])
def api_logout():
    if current_user.is_authenticated:
        security.logout_user(current_user)
    return jsonify({'success': True})


@blueprint.route('/api/check_session', methods=['POST'])
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


@blueprint.route('/api/query', methods=['PUT'])
@login_required
def api_query():
    if not request.json:
        abort(400)

    query_json = request.json['query']
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


@blueprint.route('/api/search_history', methods=['GET'])
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
        } for query in user.queries]
    })

@blueprint.route('/api/get_wordcloud_data', methods=['POST'])
@login_required
def api_get_wordcloud_data():
    if not request.json:
        abort(400)
    word_counts = analyze.make_wordcloud_data(request.json['content_list'])
    return jsonify({'data': word_counts})
