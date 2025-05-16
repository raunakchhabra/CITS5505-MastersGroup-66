# app/routes/exercise.py
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Exercisesubmission, Studylog
from datetime import datetime, timezone

exercise_bp = Blueprint('exercise_bp', __name__, url_prefix='/exercise')

@exercise_bp.route('/exercises')
def exercises():
    lang = request.args.get('lang', 'spanish') 
    return render_template('exercises.html', lang=lang)


@exercise_bp.route('/submit', methods=['POST'])
@login_required
def submit():
    data = request.get_json()
    question = data.get('question')
    user_answer = data.get('user_answer')
    correct_answer = data.get('correct_answer')
    is_correct = data.get('is_correct')

    # record the exercise submission
    submission = Exercisesubmission(
        user_id=current_user.id,
        exercise_id=0,  # set to 0 or a default value
        submitted_answer=user_answer,
        is_correct=is_correct,
        submitted_at=datetime.now(timezone.utc)
    )
    db.session.add(submission)

    # record the study log
    studylog = Studylog(
        user_id=current_user.id,
        date=datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        duration_minutes=30,  # assume 30 minutes for each exercise
        activity_type='exercise',
        skills='vocabulary',
        notes=f'Completed {question}',
        rating=3
    )
    db.session.add(studylog)

    # submit the answer to the database
    db.session.commit()

    return jsonify({
        'is_correct': is_correct,
        'message': 'Answer submitted successfully'
    })

@exercise_bp.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html', title='Forgot Password')