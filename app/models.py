from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    user_type = db.Column(db.String(10), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": user_type
    }

    def __repr__(self):
        return "User email %s" % self.email

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Student(User):
    __tablename__ = 'student'
    id = db.Column(None, db.ForeignKey('user.id'), primary_key=True)
    student_ref = db.Column(db.Integer)
    grades = db.relationship('Grade', backref='students')

    __mapper_args__ = {"polymorphic_identity": "student"}

    def __repr__(self):
        return '<Student ID: {}, name: {}>'.format(self.student_ref, self.name)


class Teacher(User):
    __tablename__ = 'teacher'
    id = db.Column(None, db.ForeignKey('user.id'), primary_key=True)
    teacher_ref = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text)
    courses = db.relationship('Course', backref='teachers')

    __mapper_args__ = {"polymorphic_identity": "teacher"}

    def __repr__(self):
        return '<Teacher {} {}>'.format(self.teacher_ref, self.title, self.name)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Text, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(Teacher.id), nullable=False)
    grades = db.relationship('Grade', backref='courses')

    def __repr__(self):
        return '<Course {}>'.format(self.code, self.name)


class Grade(db.Model):
    student_id = db.Column(db.Integer, db.ForeignKey(Student.id), nullable=False, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey(Course.id), nullable=False, primary_key=True)
    grade = db.Column(db.Text)

    def __repr__(self):
        return '<Grade {}>'.format(self.grade)
