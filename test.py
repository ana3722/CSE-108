from models import db, User
from app import app

from models import db, User
from app import app

# Replace 'new_username' and 'new_password' with the desired credentials
new_username = 'new_username'
new_password = 'new_password'  # This should be encrypted in a real application
new_role = 'student'  # Or 'teacher', 'admin', etc., depending on your User model roles

with app.app_context():
    # Check if the user already exists
    existing_user = User.query.filter_by(username=new_username).first()
    if existing_user:
        print(f'User {new_username} already exists.')
    else:
        # Create a new user instance
        new_user = User(username=new_username, password=new_password, role=new_role)
        # Add the new user to the session and commit to the database
        db.session.add(new_user)
        db.session.commit()
        print(f'Added new user: {new_user.username} with password: {new_user.password}')
