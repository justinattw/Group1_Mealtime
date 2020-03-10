from urllib.parse import urlparse, urljoin
from flask import render_template, Blueprint, request, flash, redirect, url_for, session, make_response
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError

from app import db, login_manager
from app.models import Users
from app.auth.forms import SignupForm, LoginForm, EditAccountForm

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
            flash('Incorrect password')
            return redirect(url_for('auth.login'))

        from datetime import timedelta
        login_user(user, remember=form.remember_me.data, duration=timedelta(minutes=5))

        flash('Logged in successfully. Welcome, {}'.format(user.first_name))
        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)
        return redirect(next or url_for('main.index'))
    return render_template('login.html', form=form)


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
            flash('You are now a registered user!')

            # Set cookie and return to main, if successful
            response = make_response(redirect(url_for('main.index')))
            response.set_cookie("name", form.first_name.data)
            return response
        except IntegrityError:
            db.session.rollback()
            flash('ERROR! Unable to register {}. Please check your details are correct and resubmit'.format(
                form.email.data), 'error')
    return render_template('signup.html', form=form)


@bp_auth.route('/edit_account', methods=['GET', 'POST'])
@login_required
def edit_account():
    form = EditAccountForm()

    if request.method == 'POST' and form.validate():

        user = Users.query.filter_by(id=current_user.id).first()

        if not user.check_password(form.old_password.data):
            flash('Incorrect password')
            return redirect(url_for('auth.edit_account'))

        user.set_password(form.new_password.data)
        db.session.commit()
        flash('Your password has been changed.')
        return redirect(url_for('auth.edit_account'))

    return render_template('edit_account.html',
                           form=form)


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
