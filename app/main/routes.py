from flask import render_template, Blueprint, request, flash, redirect, url_for, session, make_response
from flask_wtf.csrf import CSRFError
from markupsafe import escape
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import with_polymorphic

from app import db
from app.models import Course, Student, Teacher, User

bp_main = Blueprint('main', __name__)


@bp_main.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400


@bp_main.route('/')
def index(name=""):
    # Demonstration of use of a session cookie. Display email as the name if the session cookie is there.
    if 'name' in request.cookies:
        name = request.cookies.get('name')
    if 'name' in session:
        name= escape(session['name'])
    return render_template('index.html', name=name)


@bp_main.route('/recipes', methods=['GET'])
def recipes():
    courses = Course.query.join(Teacher).with_entities(Course.course_code, Course.name,
                                                       Teacher.name.label('teacher_name')).all()
    return render_template("recipes.html", courses=courses)


@bp_main.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        term = request.form['search_term']
        if term == "":
            flash("Enter a name to search for")
            return redirect('/')
        users = with_polymorphic(User, [Student, Teacher])
        results = db.session.query(users).filter(
            or_(users.Student.name.contains(term), users.Teacher.name.contains(term))).all()
        # results = Student.query.filter(Student.email.contains(term)).all()
        if not results:
            flash("No students found with that name.")
            return redirect('/')
        return render_template('search_results.html', results=results)
    else:
        return redirect(url_for('main.index'))

    # if request.method == 'POST':
    #     term = request.form['search_term']
    #     if term == "":
    #         flash("Enter a recipe to search for")
    #         return redirect('/')
    #
    #     results = Mealplans.query.join(MealplanRecipes).join(Track).with_entities(
    #         Artist.Name.label("ArtistName"),
    #         Album.Title,
    #         Track.Name.label("TrackName")
    #     ).filter(or_(Artist.Name.contains(term),  # or_ filter to search term for artist, album and track
    #                  Album.Title.contains(term),
    #                  Track.Name.contains(term)
    #                  )).all()
    #
    #     if not results:
    #         flash("No tracks found.")
    #         return redirect('/')
    #     return render_template('search_results.html', results=results)
    # else:
    #     return redirect(url_for('main.index'))


@bp_main.route('/delete_cookie')
def delete_cookie():
    response = make_response(redirect(url_for('main.index')))
    response.set_cookie('name', '', expires=datetime.now())
    return response


@bp_main.route('/student/<name>')
def show_student(name):
    user = Student.query.filter_by(name=name).first_or_404(description='There is no user {}'.format(name))
    return render_template('show_student.html', user=user)


# Mealplans route, query for mealplans based on logged in user_id,
# @bp_main.route('/mealplans')
# def mealplans(name):