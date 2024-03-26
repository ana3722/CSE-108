from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Course, Enrollment
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # For demonstration purposes, plaintext password comparison
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    # Assuming a many-to-many relationship between users and courses through enrollments
    enrolled_courses = Course.query.join(Enrollment, Course.id == Enrollment.course_id).filter(Enrollment.student_id == user.id)
    courses = Course.query.all()
    return render_template('dashboard.html', user=user, courses=courses, enrolled_courses=enrolled_courses)

@app.route('/enroll/<int:course_id>', methods=['POST'])
def enroll(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Check if the user is already enrolled
    existing_enrollment = Enrollment.query.filter_by(student_id=session['user_id'], course_id=course_id).first()
    if existing_enrollment:
        flash('You are already enrolled in this course!')
    else:
        enrollment = Enrollment(student_id=session['user_id'], course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
        flash('You have been enrolled!')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    if not os.path.exists('school.db'):
        with app.app_context():
            db.create_all()  # This will create the database file and tables if they don't exist
    app.run(debug=True)
