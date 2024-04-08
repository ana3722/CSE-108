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
        # Query the user by username
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # In production, use hashed passwords
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

# Define the route for logging out
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

# Define the route for the user dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    # Implement dashboard logic, e.g., listing courses, enrolling in courses
    return render_template('dashboard.html', user=user)

# Define the route for enrolling in a course
@app.route('/enroll/<int:course_id>', methods=['POST'])
def enroll(course_id):
    # Implement enrollment logic
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates the database tables if they don't exist
    app.run(debug=True)
