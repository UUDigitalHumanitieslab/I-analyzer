import warnings

import flask_admin as admin
from flask_admin.base import MenuLink

from ianalyzer import models
from . import views

admin_instance = admin.Admin( 
    name='IAnalyzer', index_view=views.AdminIndexView(), endpoint='admin')

admin_instance.add_link(MenuLink(name='Frontend', category='', url="/home"))

# this wrapper makes sure we don't get the warning caused by removing the password field
# from the 'edit user' view
with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'Fields missing from ruleset', UserWarning)
    admin_instance.add_view(views.UserView(
        models.User, models.db.session, name='Users', endpoint='users'))

admin_instance.add_view(views.RoleView(
    models.Role, models.db.session, name='Roles', endpoint='roles'))

admin_instance.add_view(views.CorpusView(
    models.Corpus, models.db.session, name='Corpora', endpoint='corpus'))

admin_instance.add_view(views.QueryView(
    models.Query, models.db.session, name='Queries', endpoint='queries'))