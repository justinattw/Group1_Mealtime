from urllib.parse import urlparse, urljoin

from flask import render_template, Blueprint, request, flash, redirect, url_for, make_response, abort
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError

from app import db, login_manager
from app.auth.forms import SignupForm, LoginForm, EditPasswordForm, EditPreferencesForm
from app.models import Users, UserAllergies, UserDietPreferences

bp_auth = Blueprint('auth', __name__)


@bp_auth.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('No account has been registered with this email.')
            return redirect(url_for('auth.login'))

        if not user.check_password(form.password.data):
            flash('Incorrect password.')
            return redirect(url_for('auth.login'))

        from datetime import timedelta
        login_user(user, remember=form.remember_me.data, duration=timedelta(minutes=5))

        flash('Logged in successfully. Welcome, {}'.format(user.first_name))
        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)
        return redirect(next or url_for('main.index'))
    return render_template('auth/login.html', form=form)


@bp_auth.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@bp_auth.route('/signup/', methods=['POST', 'GET'])
def signup():
    form = SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        user = Users(first_name=form.first_name.data,
                     last_name=form.last_name.data,
                     email=form.email.data)
        user.set_password(form.password.data)

        try:
            db.session.add(user)
            db.session.commit()

            user_id, = db.session.query(Users.id).filter_by(email=form.email.data).first()
            # Set user preferences to classic by default
            diet_preference = UserDietPreferences(user_id=user_id, diet_type_id=1)
            db.session.add(diet_preference)
            db.session.commit()

            login_user(user)

            flash('You are now a registered user!')

            # Set cookie and return to main, if successful
            response = make_response(redirect(url_for('main.index')))
            response.set_cookie("name", form.first_name.data)
            return response
        except IntegrityError:
            db.session.rollback()
            flash('ERROR! Unable to register {}. Please check your details are correct and resubmit.'.format(
                form.email.data), 'error')
    return render_template('auth/signup.html', form=form)


@bp_auth.route('/account/')
@login_required
def account():
    user = Users.query.filter_by(id=current_user.id).first_or_404(
        description='There is no user {}'.format(current_user.id))
    return render_template('auth/account.html', user=user)


@bp_auth.route('/edit_password/', methods=['GET', 'POST'])
@login_required
def edit_password():
    form = EditPasswordForm()

    if request.method == 'POST' and form.validate():

        user = Users.query.filter_by(id=current_user.id).first()

        if not user.check_password(form.old_password.data):
            flash('Incorrect old password')
            return redirect(url_for('auth.edit_password'))

        user.set_password(form.new_password.data)
        db.session.commit()
        flash('Your password has been changed.')
        return redirect(url_for('auth.account'))

    return render_template('auth/edit_account/edit_password.html', form=form)


@bp_auth.route('/edit_preferences/', methods=['GET', 'POST'])
@login_required
def edit_preferences():
    form = EditPreferencesForm()

    if request.method == 'POST':
        user_id = current_user.id

        # Turn allergy list into integers
        allergy_list = list(map(int, form.allergies.data))
        diet_type_id = int(form.diet_type.data)

        try:
            # Remove all diet preferences for user
            UserDietPreferences.query.filter_by(user_id=user_id).delete()
            UserAllergies.query.filter_by(user_id=user_id).delete()

            # Re-add diet_preference
            db.session.add(UserDietPreferences(user_id=user_id, diet_type_id=diet_type_id))

            # For each allergy identified, add to db
            for allergy_id in allergy_list:
                db.session.add(UserAllergies(user_id=user_id, allergy_id=allergy_id))

            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash('ERROR! Unable to make preference changes. Please try again.')

        flash('Your food preferences have been updated.')
        return redirect(url_for('auth.account'))

    return render_template('auth/edit_account/edit_preferences.html', form=form)


# A public user profile viewer
@bp_auth.route('/favourites')
@login_required
def favourites():
    user = Users.query.filter_by(id=current_user.id) \
        .first_or_404(description='There is no user {}'.format(current_user.id))
    return render_template('auth/favourites.html', user=user)


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
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth.login'))
