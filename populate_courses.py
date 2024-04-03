from models import db, Course
from app import app

courses_data = [
    {"name": "Mathematics", "code": "MATH101", "teacher_id": 1},
    {"name": "Physics", "code": "PHYS101", "teacher_id": 2},
    # Add more courses as needed
]

with app.app_context():
    for course_info in courses_data:
        course = Course.query.filter_by(code=course_info["code"]).first()
        if not course:
            new_course = Course(**course_info)
            db.session.add(new_course)
            db.session.commit()
            print(f'Added new course: {new_course.name} ({new_course.code})')
