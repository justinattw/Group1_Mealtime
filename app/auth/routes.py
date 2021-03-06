#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app/auth/routes.py:

This document includes WTForms for authentication methods.
Authentication methods include signup, login, edit account details and log out.
"""
__authors__ = "Ethan Low, Danny Wallis, Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Ethan Low", "Danny Wallis", "Justin Wong"]
__status__ = "Development"

from app import db, login_manager
from app.auth.forms import SignupForm, LoginForm, EditPasswordForm, EditPreferencesForm
from app.models import Users, UserAllergies, UserDietPreferences

from flask import render_template, Blueprint, request, flash, redirect, url_for, make_response, abort
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from urllib.parse import urlparse, urljoin

bp_auth = Blueprint('auth', __name__)


@bp_auth.route('/login/', methods=['GET', 'POST'])
def login():
    """
    Login route allowing users to sign into the application to access its services.

    :return:
    """
    form = LoginForm()

    if request.method == 'POST' and form.validate():

        # Check if email has already been previously registered
        # at the moment we don't turn email to lower case, so mis-matched cases will not be verified
        user = Users.query.filter_by(email=(form.email.data).lower()).first()

        if user is None:
            flash('No account has been registered with this email.', 'warning')
            return redirect(url_for('auth.login'))

        if not user.check_password(form.password.data):
            flash('Incorrect password.', 'danger')
            return redirect(url_for('auth.login'))

        from datetime import timedelta
        login_user(user, remember=form.remember_me.data, duration=timedelta(minutes=5))

        flash(f'Logged in successfully. Welcome, {user.first_name}!', 'success')
        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)
        return redirect(next or url_for('main.index'))
    return render_template('auth/login.html', form=form)


@bp_auth.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))


@bp_auth.route('/signup/', methods=['POST', 'GET'])
def signup():
    form = SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        user = Users(first_name=form.first_name.data,
                     last_name=form.last_name.data,
                     email=(form.email.data).lower())
        user.set_password(form.password.data)

        try:
            db.session.add(user)

            diet_preference = UserDietPreferences(diet_type_id=1)
            user.diet_preferences.append(diet_preference)  # Add diet_preference to current user

            db.session.commit()

            login_user(user)  # User is logged in upon signing up
            flash('You are now a registered user!', 'success')

            response = make_response(redirect(url_for('main.index')))  # Set cookie and return to main, if successful
            response.set_cookie("name", form.first_name.data)
            return response

        except IntegrityError:
            # Validations in forms are already done (e.g. email is already registered), this error probably can't be
            # triggered from frontend.
            db.session.rollback()
            flash(f'ERROR! Unable to register {form.email.data}. Please check your details are correct and resubmit.',
                  'danger')

    return render_template('auth/signup.html', form=form)


@bp_auth.route('/account/')
@login_required
def account():
    """
    Shows a logged-in user their account details

    :return: template for account.html
    """
    user = Users.query.filter_by(id=current_user.id).first_or_404(description=f'There is no user {current_user.id}')

    return render_template('auth/account.html', user=user)


@bp_auth.route('/edit_password/', methods=['GET', 'POST'])
@login_required
def edit_password():
    """
    Allows a logged-in user to change their password by verifying their old password and validating their new passwords.

    :return: edit_password route if check_password fails, or account route if edit_password is a success.
    """
    form = EditPasswordForm()

    if request.method == 'POST' and form.validate():

        user = Users.query.filter_by(id=current_user.id).first()

        if not user.check_password(form.old_password.data):
            flash('Incorrect old password', 'warning')
            return redirect(url_for('auth.edit_password'))

        user.set_password(form.new_password.data)

        try:
            db.session.commit()
            flash('Your password has been changed.', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('ERROR! Unable to change your password, please check your details are correct and try again.',
                  'warning')

        return redirect(url_for('auth.account'))

    return render_template('auth/edit_account/edit_password.html', form=form)


@bp_auth.route('/edit_preferences/', methods=['GET', 'POST'])
@login_required
def edit_preferences():
    form = EditPreferencesForm()

    user = Users.query.filter_by(id=current_user.id).first_or_404(
        description='There is no user {}'.format(current_user.id))

    if request.method == 'POST':

        allergy_list = list(map(int, form.allergies.data))  # Turn form's allergy list from strings to ints
        diet_type_id = int(form.diet_type.data)

        try:
            # Remove all diet preferences for user to overwrite pre-existing settings
            UserDietPreferences.query.filter_by(user_id=user.id).delete()
            UserAllergies.query.filter_by(user_id=user.id).delete()

            # Add newly set diet preferences and allergies to current user
            diet_type = UserDietPreferences(diet_type_id=diet_type_id)
            user.diet_preferences.append(diet_type)

            for allergy_id in allergy_list:
                allergy = UserAllergies(allergy_id=allergy_id)
                user.allergies.append(allergy)

            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash('ERROR! Unable to make preference changes. Please try again.', 'danger')

        flash('Your food preferences have been updated.', 'success')
        return redirect(url_for('auth.account'))

    return render_template('auth/edit_account/edit_preferences.html', form=form)


def is_safe_url(target):
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in ('http', 'https') and host_url.netloc == redirect_url.netloc


def get_safe_redirect():
    url = request.args.get('next')
    if url and is_safe_url(url):
        return url
    url = request.referrer
    if url and is_safe_url(url):
        return url
    return '/'


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return Users.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.', 'warning')
    return redirect(url_for('auth.login'))
