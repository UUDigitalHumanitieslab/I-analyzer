#!/usr/bin/env python3

import sys
import logging
from datetime import datetime

from flask import Flask
from werkzeug.security import generate_password_hash
from sqlalchemy import exc
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Command, Option

from ianalyzer.corpora import corpora
from ianalyzer import config
from ianalyzer.models import User, Role, db
from ianalyzer.web import blueprint, admin_instance, login_manager
from ianalyzer.factories import flask_app, elasticsearch
from es_index import perform_indexing


def ctx():
    app = flask_app(blueprint, admin_instance, login_manager)
    return app


def create_admin(pwd)
    with ctx().app_context():

        role_admin = Role('admin', 'Administrator role.')
        role_corpus_user = Role(config.CORPUS, 'Role for users who may access '+config.CORPUS+' data.')

        username = 'admin'
        password = pwd
            
        admin = User.query.filter_by(username='admin').first()
            
        if admin:
            admin.password = generate_password_hash(password)
        else:
            user = User(username, generate_password_hash(password))
            user.roles.append(role_admin)
            user.roles.append(role_corpus_user)
            db.session.add(user)
            db.session.add(role_admin)
            db.session.add(role_corpus_user)
            
        return db.session.commit()


def migrations():
    ''' initialize migration
    options: init, migrate
    run after database models change
    can be accessed through the MigrationsCommand interface
    '''
    with ctx().app_context():
        migrate = Migrate(app, db)


class AdminCommand(Command):
    '''(re)sets admin password'''
    option_list = (
        Option('--password', 
            '-p', 
            dest='pwd', 
            help='Set administrator password'
            ),
    )

    def run(self, pwd):
        create_admin(pwd)


class IndexingCommand(Command):
    ''' perform elastic search indexing on the data source 
    specified in config.py'''

    option_list = (
        Option('--corpus', 
            '-c', 
            dest='corpus', 
            help='Sets which corpus should be indexed' +
                'Options: times or dutchbanking' +
                'If not set, corpus defined in config.py will be indexed'
            ),
        Option('--start', 
            '-s', 
            dest='start', 
            help='Set the date where indexing should start.' +
                'The input format is YYYY-MM-DD.' + 
                'If not set, indexing will start from corpus minimum date.'
            ),
        Option('--end', 
            '-e', 
            dest='end', 
            help='Set the date where indexing should end' + 
                'The input format is YYYY-MM-DD.' +
                'If not set, indexing will start from corpus maximum date.'
            ),
    )

    def run(self, corpus, start, end):
        
        if not corpus:
            corpus = config.CORPUS
        
        corpus = corpora[corpus]

        try:
            if not start:
                start_index = corpus.min_date
            else:
                start_index = datetime.strptime(start, '%Y-%m-%d')
            
            if not end:
                end_index = corpus.max_date
            else:
                end_index = datetime.strptime(end, '%Y-%m-%d')  

            print (start_index, end_index)
            
        except Exception:
            logging.critical(
                'Incorrect data format '
                'Example call: manage.py es -c times -s 1785-01-01 -e 2010-12-31'
            )
            raise
        
        perform_indexing(corpus, start_index, end_index)


if __name__ == '__main__':
    logging.basicConfig(level=config.LOG_LEVEL)
    app = flask_app(blueprint, admin_instance, login_manager)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)
    manager.add_command('admin', AdminCommand)
    manager.add_command('es', IndexingCommand)
    manager.run()
