from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Course, Enrollment
import os
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)


admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Course, db.session))
admin.add_view(ModelView(Enrollment, db.session))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # For demonstration only; use hashed passwords in production
            session['user_id'] = user.id
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    enrolled_courses = Course.query.join(Enrollment, Course.id == Enrollment.course_id).filter(
        Enrollment.student_id == user.id).all()
    courses = Course.query.all()
    # Add capacity and enrolled count to the courses
    for course in courses:
        course.capacity = 10  # Assuming each course has a capacity of 10 students
        course.students_enrolled = Enrollment.query.filter_by(course_id=course.id).count()
    return render_template('dashboard.html', user=user, courses=courses, enrolled_courses=enrolled_courses)

@app.route('/enroll/<int:course_id>', methods=['POST'])
def enroll(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Check if the user is already enrolled
    existing_enrollment = Enrollment.query.filter_by(student_id=session['user_id'], course_id=course_id).first()
    if existing_enrollment:
        flash('You are already enrolled in this course!', 'info')
    else:
        # Check if the course has reached its capacity
        enrolled_count = Enrollment.query.filter_by(course_id=course_id).count()
        if enrolled_count < 10:  # Assuming each course has a capacity of 10 students
            enrollment = Enrollment(student_id=session['user_id'], course_id=course_id)
            db.session.add(enrollment)
            db.session.commit()
            flash('You have been enrolled!', 'success')
        else:
            flash('This course has reached its capacity.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    if not os.path.exists('school.db'):
        with app.app_context():
            db.create_all()  # This will create the database file and tables if they don't exist
    app.run(debug=True)
