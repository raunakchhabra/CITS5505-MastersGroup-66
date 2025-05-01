from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')
