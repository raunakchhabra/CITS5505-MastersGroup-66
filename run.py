from flask import Flask, request, jsonify, render_template, url_for, redirect, session
import sqlite3
import bcrypt
import jwt
import datetime
import smtplib
from email.mime.text import MIMEText
from config import Config
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import requests
import os

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# Google OAuth 2.0 configuration
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # For development only, allows HTTP
GOOGLE_CLIENT_ID = "your-Google-ID"  # from Google Cloud Console 
client_secrets_file = os.path.join(os.getcwd(), "client_secrets.json")  # need Google client secrets file
SCOPES = ["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile", "openid"]

# Initialize SQLite database
def init_db():
    with sqlite3.connect(app.config['DATABASE']) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reset_tokens (
                email TEXT NOT NULL,
                token TEXT NOT NULL,
                expires_at INTEGER NOT NULL
            )
        ''')
        conn.commit()

# Get a database connection
def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# Check if user is logged in
def is_logged_in():
    return 'user_email' in session

# Home page route
@app.route('/')
@app.route('/index.html')
def index_page():
    return render_template('index.html', is_logged_in=is_logged_in())

# Google OAuth login route
@app.route('/auth/google')
def google_login():
    flow = Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=SCOPES,
        redirect_uri=url_for('google_callback', _external=True)
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

# Google OAuth callback route
@app.route('/auth/google/callback')
def google_callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('google_callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    id_info = id_token.verify_oauth2_token(
        credentials.id_token,
        Request(),
        GOOGLE_CLIENT_ID
    )

    email = id_info['email']
    name = id_info.get('name', email.split('@')[0])

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()

        if not user:
            dummy_password = "google_oauth_user"
            hashed_password = bcrypt.hashpw(dummy_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                          (name, email, hashed_password))
            conn.commit()

    session['user_email'] = email
    return redirect('/dashboard.html')

# Register a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                          (name, email, hashed_password))
            conn.commit()
        return jsonify({'message': 'Successful registration!'}), 200
    except sqlite3.IntegrityError:
        return jsonify({'error': 'This email has been registered.'}), 400

# Authenticate a user during login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        session['user_email'] = email
        return jsonify({'message': 'Successful login!'}), 200
    else:
        return jsonify({'error': 'Email or password error!'}), 401

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect('/login.html')

# Handle password reset requests
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()

    if not user:
        return jsonify({'error': 'This email is not registered'}), 404

    expires_at = int((datetime.datetime.utcnow() + datetime.timedelta(hours=1)).timestamp())
    token = jwt.encode({'email': email, 'exp': expires_at}, app.config['SECRET_KEY'], algorithm='HS256')

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO reset_tokens (email, token, expires_at) VALUES (?, ?, ?)',
                      (email, token, expires_at))
        conn.commit()

    reset_link = f"http://127.0.0.1:5000/reset-password.html?token={token}"
    message = MIMEText(f'Click the following link to reset your password: {reset_link}\nThe link will expire in 1 hour.')
    message['Subject'] = 'Password Reset - PolyLingua'
    message['From'] = app.config['MAIL_USERNAME']
    message['To'] = email

    with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.send_message(message)
    return jsonify({'message': 'Password reset link has been sent! Please check your email.'}), 200

# Process password reset
@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('newPassword')

    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        email = payload['email']

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM reset_tokens WHERE token = ? AND email = ?', (token, email))
            token_record = cursor.fetchone()

        if not token_record:
            return jsonify({'error': 'Reset link is invalid or has expired!'}), 400

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET password = ? WHERE email = ?', (hashed_password, email))
            cursor.execute('DELETE FROM reset_tokens WHERE email = ?', (email,))
            conn.commit()

        return jsonify({'message': 'Password reset successful! Please login.'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Reset link has expired!'}), 400
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Reset link is invalid!'}), 400

# Route to render pages
@app.route('/login.html')
def login_page():
    if is_logged_in():
        return redirect('/dashboard.html')
    return render_template('login.html')

@app.route('/register.html')
def register_page():
    if is_logged_in():
        return redirect('/dashboard.html')
    return render_template('register.html')

@app.route('/forgot-password.html')
def forgot_password_page():
    if is_logged_in():
        return redirect('/dashboard.html')
    return render_template('forgot-password.html')

@app.route('/reset-password.html')
def reset_password_page():
    if is_logged_in():
        return redirect('/dashboard.html')
    return render_template('reset-password.html')

@app.route('/dashboard.html')
def dashboard_page():
    #if not is_logged_in():   // comment out just for testing
        #return redirect('/login.html') // comment out just for testing
    return render_template('dashboard.html')

@app.route('/profile.html')
def profile_page(): #comment out just for testing below
    #if not is_logged_in():
        #return redirect('/login.html')
    #with get_db() as conn:
        #cursor = conn.cursor()
        #cursor.execute('SELECT * FROM users WHERE email = ?', (session['user_email'],))
        #user = cursor.fetchone()
    #return render_template('profile.html', user=user)
    return render_template('profile.html') 
@app.route('/settings.html')
def settings_page(): 
    #if not is_logged_in():
        #return redirect('/login.html')
    return render_template('settings.html')

@app.route('/exercises.html')
def exercises():
    return render_template('exercises.html')

@app.route('/community.html')
def community():
    return render_template('community.html')

@app.route('/about.html')
def about():
    return render_template('about.html')
@app.route('/progress-report.html')
def progress_report_page(): #comment out just for testing below
    #if not is_logged_in():
        #return redirect('/login.html')
    return render_template('progress-report.html')

@app.route('/upload-data.html')
def upload_data_page(): #comment out just for testing below
    #if not is_logged_in():
        #return redirect('/login.html')
    return render_template('upload-data.html')

@app.route('/visualize-data.html')
def visualize_data_page(): #comment out just for testing below
    #if not is_logged_in():
        #return redirect('/login.html')
    return render_template('visualize-data.html')

@app.route('/share-data.html')
def share_data_page(): #comment out just for testing below
    #if not is_logged_in():
        #return redirect('/login.html')
    return render_template('share-data.html')
@app.route('/courses.html')
def courses_page():
    if 'user_email' in session:
        # Fetch user data from database based on session['user_email']
        # For example:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM users WHERE email = ?', (session['user_email'],))
            user = cursor.fetchone()
            username = user['name'] if user else 'User'
        return render_template('courses.html', username=username)
    else:
        return render_template('courses.html', username='User') # Default if not logged in
    
if __name__ == '__main__':
    init_db()
    app.run(debug=True)