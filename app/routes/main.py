#main.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Exercise, Exercisesubmission, Progress, Studylog
from app.extensions import db
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    return render_template('index.html', title='Home')

# new route for demo by Julie 11 MAY 2025
@main_bp.route('/about')
def about():
    return render_template('about.html', title='About Us')

@main_bp.route('/community')
def community():
    return render_template('community.html', title='Community')

@main_bp.route('/courses')
def courses():
    return render_template('courses.html', title='Courses')


@main_bp.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html', title='Forgot Password')

@main_bp.route('/profile')
@login_required
def profile():
    # calculate the total learning time in hours
    total_learning_time = sum(log.duration_minutes for log in current_user.studylogs) // 60 if current_user.studylogs else 0
    
    # languages the user is learning
    languages = ', '.join(lang.language for lang in current_user.user_languages) if current_user.user_languages else 'None'
    
    return render_template(
        'profile.html',
        user=current_user,
        total_learning_time=total_learning_time,
        languages=languages
    )
@main_bp.route('/progress-report')
def progress_report():
    return render_template('progress-report.html', title='Progress Report')

@main_bp.route('/reset-password')
def reset_password():
    return render_template('reset-password.html', title='Reset Password')

@main_bp.route('/settings')
def settings():
    return render_template('settings.html', title='Settings')
