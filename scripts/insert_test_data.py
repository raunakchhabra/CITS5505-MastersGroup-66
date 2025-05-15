# scripts/insert_test_data.py
import sys
import os
# to ensure the script can find the app module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models import User, Data, SharedData, DataType, SharedPermission
from app.models import Progress, Studylog
from datetime import datetime, timedelta

app = create_app()
with app.app_context():
    # check if user exists
    user_id = 1
    user = User.query.get(user_id)
    if not user:
        print(f"User with ID {user_id} does not exist. Please create a user first.")
        user = User(name="Test User", email="test@example.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        print(f"Created new user with ID {user_id}")

    # to delete existing test data
    Progress.query.filter_by(user_id=user_id).delete()
    Studylog.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    # insert test data
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).date()
        date_str = date.strftime('%Y-%m-%d')
        progress = Progress(
            user_id=user_id,
            course_id=1,
            date=date_str,
            listening=50 + i,
            reading=60 + i,
            speaking=40 + i,
            writing=55 + i,
            vocabulary_count=100 + i * 10,
            level='B1',
            total_study_hours='10'
        )
        studylog = Studylog(
            user_id=user_id,
            date=date_str,
            duration_minutes=30,
            activity_type='practice',
            skills='reading,writing,vocabulary',
            notes='Test',
            rating=3
        )
        db.session.add(progress)
        db.session.add(studylog)
    db.session.commit()
    print("Test data inserted successfully.")

if __name__ == '__main__':
    app.run(debug=True)