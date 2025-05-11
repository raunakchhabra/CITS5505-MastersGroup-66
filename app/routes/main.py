#main.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@main_bp.route('/dashboard')
def dashboard():  #  No login_required for demo
    return render_template('dashboard.html', title='Dashboard')

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

@main_bp.route('/exercises')
def exercises():
    return render_template('exercises.html', title='Exercises')

@main_bp.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html', title='Forgot Password')

@main_bp.route('/profile')
def profile():
    return render_template('profile.html', title='Profile')

@main_bp.route('/progress-report')
def progress_report():
    return render_template('progress-report.html', title='Progress Report')

@main_bp.route('/reset-password')
def reset_password():
    return render_template('reset-password.html', title='Reset Password')

@main_bp.route('/settings')
def settings():
    return render_template('settings.html', title='Settings')

@main_bp.route('/share-data')
def share_data():
    return render_template('share_data.html', title='Share Data')

@main_bp.route('/visualize-data')
def visualize_data():
    return render_template('visualize-data.html', title='Visualize Data')