'''
For creation of Flask and ElasticSearch objects.
'''
import os
import logging

from flask import Flask
from flask_mail import Mail
from flask_login import LoginManager
from flask_seasurf import SeaSurf

from api import api, mail #blueprint and mail object
from ianalyzer.models import db
from admin.admin import admin_instance
from ianalyzer.views import entry, login_manager
from es.es_forward import es #blueprint
from saml.views import saml_auth # DHLab wrapper around python3-saml
from saml import saml # blueprint
from wordmodels.views import wordmodels #blueprint

from ianalyzer import config_fallback as config
from ianalyzer import celery_app
from ianalyzer.factories.celery import init_celery

def flask_app(cfg=config):
    '''
    Create Flask instance, with given configuration and flask_admin, flask_login,
    and csrf (SeaSurf) instances.
    '''
    logging.info("initializing app...")
    app = Flask(__name__)

    app.config.from_object(cfg)
    csrf = SeaSurf()
    csrf.exempt_urls(('/es', '/saml'))
    init_celery(app, celery=celery_app)

    app.register_blueprint(entry)
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(es, url_prefix='/es')
    app.register_blueprint(saml, url_prefix='/saml')
    app.register_blueprint(wordmodels, url_prefix='/wordmodels')

    db.init_app(app)
    login_manager.init_app(app)
    admin_instance.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    saml_auth.init_app(app)

    return app

