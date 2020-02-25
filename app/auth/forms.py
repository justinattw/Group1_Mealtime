from flask_wtf import FlaskForm
from sqlalchemy import or_
from sqlalchemy.orm import with_polymorphic
from wtforms import StringField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError

from app import db
from app.models import Student, User, Teacher


class SignupForm(FlaskForm):
    title = SelectField('Title', choices=[('mr', 'Mr'), ('mrs', 'Mrs'), ('dr', 'Dr'), ('prof', 'Prof')])
    name = StringField('Name', validators=[DataRequired()])
    role = SelectField('Role', choices=[('student', 'Student'), ('teacher', 'Teacher')])
    uni_id = StringField('University ID number', validators=[DataRequired(message="University ID number required")])
    email = StringField('Email address', validators=[DataRequired(), Email(message='Valid email address required')])
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')

    def validate_uni_id(self, uni_id):
        users = with_polymorphic(User, [Student, Teacher])
        results = db.session.query(users).filter(
            or_((users.Student.student_ref == uni_id.data), (users.Teacher.teacher_ref == uni_id.data))).first()
        # student = Student.query.filter_by(student_ref=id_value.data).first()
        if results is not None:
            raise ValidationError('An account is already registered for that university ID')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
