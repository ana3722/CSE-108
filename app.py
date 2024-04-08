from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from wtforms import StringField
from models import db, User, Course, Enrollment
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SECRET_KEY'] = 'your_secret_key'

# Deferred initialization of SQLAlchemy
db.init_app(app)

# Initialize Flask-Admin to work with the app
admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')

# Flask-Admin views
class UserAdminView(ModelView):
    column_list = ('username', 'role')
    column_searchable_list = ('username',)

class CourseAdminView(ModelView):
    column_list = ('name', 'code', 'teacher_id')
    column_searchable_list = ('name', 'code')
    form_columns = ('name', 'code', 'teacher_id')
    form_extra_fields = {
        'teacher_id': StringField('Teacher')
    }

# Add admin views to Flask-Admin
admin.add_view(UserAdminView(User, db.session))
admin.add_view(CourseAdminView(Course, db.session))

# Define the route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Define the route for logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # Use hashed passwords in production
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

# Define the route for logging out
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('home'))

# Define the route for the user dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role') == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    elif session.get('role') == 'admin':
        return redirect('/admin')
    # Default to a general dashboard for students or other roles
    return render_template('dashboard.html')

# Define the route for the teacher dashboard
@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login'))
    user_id = session['user_id']
    courses = Course.query.filter_by(teacher_id=user_id).all()
    for course in courses:
        course.enrollments = Enrollment.query.filter_by(course_id=course.id).all()
    return render_template('teacher_dashboard.html', courses=courses)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
