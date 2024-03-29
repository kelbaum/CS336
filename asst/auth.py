'''Module for authentication and authorization

Uses the flask-login plugin as well as some custom wrapper functions to ensure
that logged in users are only able to access authorized resources.
'''
from functools import wraps
import flask
from flask import Blueprint, render_template, url_for, redirect, flash
import flask_login
import sys, traceback
from asst import LM as login_manager
from asst.models import User
from werkzeug.security import check_password_hash

auth_pages = Blueprint('auth_pages', __name__, template_folder="./views/templates")

@login_manager.user_loader
def user_loader(email):
    '''Loads the user via a DB call

    Args:
        email (str): The email to load

    Returns:
        User: The user object corresponding to the email passed, or None if it doesn't exist
    '''
    try:
        users = User.select().where(User.Email == email)
        if len(users) > 0:
            return users[0]
        else:
            return
    except Exception as e:
        traceback.print_exc(file=sys.stdout)

@login_manager.unauthorized_handler
def unauth():
    '''Function to handle requests to resources that are not authorized or authenticated.'''
    return render_template('unauthorized.html'), 401

def require_login(func):
    '''Wrapper around the login_required wrapper from flask-login

    This allows us to keep the same style and also not have to have multiple imports for
    roles and require_login
    '''
    @wraps(func)
    @flask_login.login_required
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper

def require_role(role,**kwargss):
    '''Decorate a function with this in order to require a specific role(s), to access a view.

    Also decorates a function, so that you must pass the current user's role into it's first
    argument if it's needed.

    By decorating a function with @require_role you are implicity forcing @login_required as well.
    Example:

    .. code-block:: python

        @APP.route('/admin-dashboard')
        @require_role('admin')
        def view_dash():
        # Something here

        @APP.route('/reservationH')
        @require_role('admin','host',getrole=True)
        def view_dash(role):
            ...

    Args:
        role(list or str):  A single role name or list of role names for which users are allowed to access the specified resource

    If a user is not authorized then the flask_login.unauthorized handler is called.
    '''
    def real_wrap(func):
        @wraps(func)
        @flask_login.login_required
        def wrapper(*args, **kwargs):
            user = flask_login.current_user
            if kwargss.get('getrole', False):
                args = tuple([user.role])
            if isinstance(role, list) and user.role in role:
                return func(*args, **kwargs)
            elif user.role == role:
                return func(*args, **kwargs)
            else:
                return login_manager.unauthorized()
        return wrapper
    return real_wrap

@auth_pages.route('/login', methods=['GET', 'POST'])
def login():
    '''Logs a user into the application'''
    try:
        if flask_login.current_user.is_authenticated:
            return redirect(url_for('index'))

        if flask.request.method == 'GET':
            return render_template('login.html', logged_in = False)

        email = flask.request.form['email']
        users = User.select().where(User.Email == email)

        if len(users) <= 0:
            flash('Unable to login user {}'.format(email), 'danger')
            return render_template('login.html', logged_in = False)
        else:
            user = users[0]

        if check_password_hash(user.password, flask.request.form['pw']):
            user.id = user.Email
            flask_login.login_user(user)
            return flask.redirect(flask.url_for('index'))

        # Last resort - just return an error about logging in
        flash('Unable to login user {}'.format(email), 'danger')
    except Exception as e: 
        traceback.print_exc(file=sys.stdout)
        flash('Registration failed: ' + str(e), 'danger')
    return render_template('login.html' , logged_in = False), 401

@auth_pages.route('/logout')
def logout():
    ''''Logs a user out and renders the login template with a message'''
    flask_login.logout_user()
    flash("Successfully logged out", 'success')
    return render_template('login.html' , logged_in = False)