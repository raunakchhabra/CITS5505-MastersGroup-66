# run.py
from flask import Flask, request, jsonify, render_template, url_for
import sqlite3
import bcrypt
import jwt
import datetime
import smtplib
from email.mime.text import MIMEText
from config import Config

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config.from_object(Config)

# Initialize SQLite database
# 
# Assumptions:
# - The database path is specified in the Config object (app.config['DATABASE']).
# - SQLite is used as the database backend.
# 
# Preconditions:
# - The Config object must have a valid 'DATABASE' key pointing to a file path.
# - The application must have write permissions to the database file path.
# 
# Inputs:
# - None
# 
# Outputs:
# - Creates two tables in the database if they don't exist:
#   - 'users': Stores user information (id, name, email, password).
#   - 'reset_tokens': Stores password reset tokens (email, token, expires_at).
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
#
# Assumptions:
# - The database has been initialized using init_db().
# - The database file exists at the path specified in app.config['DATABASE'].
#
# Preconditions:
# - init_db() must have been called to create the necessary tables.
#
# Inputs:
# - None
#
# Outputs:
# - Returns a SQLite connection object with row_factory set to sqlite3.Row for dictionary-like row access.
def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# Register a new user
#
# Assumptions:
# - The request contains JSON data with 'name', 'email', and 'password' fields.
# - The email provided is unique (not already registered).
#
# Preconditions:
# - The database must be initialized (init_db() called).
# - The request must be a POST request with a JSON body.
#
# Inputs:
# - JSON object with:
#   - name (str): The user's full name.
#   - email (str): The user's email address.
#   - password (str): The user's password (will be hashed before storage).
#
# Outputs:
# - Success: Returns a JSON response with a 'message' field and HTTP status 200.
# - Failure:
#   - If required fields are missing: Returns {'error': 'All fields are required'}, HTTP 400.
#   - If email already exists: Returns {'error': 'This email has been registered.'}, HTTP 400.
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    # Password encryption using bcrypt
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
#
# Assumptions:
# - The request contains JSON data with 'email' and 'password' fields.
# - The password is stored in the database as a bcrypt hash.
#
# Preconditions:
# - The database must be initialized (init_db() called).
# - The request must be a POST request with a JSON body.
#
# Inputs:
# - JSON object with:
#   - email (str): The user's email address.
#   - password (str): The user's password (to be verified against the stored hash).
#
# Outputs:
# - Success: Returns a JSON response with a 'message' field and HTTP status 200.
# - Failure: Returns {'error': 'Email or password error!'}, HTTP 401.
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
        return jsonify({'message': 'Successful login!'}), 200
    else:
        return jsonify({'error': 'Email or password error!'}), 401

# Handle password reset requests
#
# Assumptions:
# - The request contains JSON data with an 'email' field.
# - The email exists in the users table.
# - Email sending is configured in Config (though currently simulated).
#
# Preconditions:
# - The database must be initialized (init_db() called).
# - The request must be a POST request with a JSON body.
# - Config must have 'SECRET_KEY', 'MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', and 'MAIL_PASSWORD'.
#
# Inputs:
# - JSON object with:
#   - email (str): The user's email address to send the reset link to.
#
# Outputs:
# - Success: Returns a JSON response with a 'message' field and HTTP status 200.
# - Failure:
#   - If email is not registered: Returns {'error': 'This email is not registered'}, HTTP 404.
#   - If email sending fails: Simulates success and logs the reset link to the console.
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

    # Generate a JWT token for password reset, valid for 1 hour
    expires_at = int((datetime.datetime.utcnow() + datetime.timedelta(hours=1)).timestamp())
    token = jwt.encode({'email': email, 'exp': expires_at}, app.config['SECRET_KEY'], algorithm='HS256')

    # Store the token in the reset_tokens table
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO reset_tokens (email, token, expires_at) VALUES (?, ?, ?)',
                      (email, token, expires_at))
        conn.commit()

    # Simulate sending an email with the reset link
    reset_link = f"http://127.0.0.1:5000/reset-password.html?token={token}"
    message = MIMEText(f'Click the following link to reset your password: {reset_link}\nThe link will expire in 1 hour.')
    message['Subject'] = 'Password Reset - PolyLingua'
    message['From'] = app.config['MAIL_USERNAME']
    message['To'] = email

    try:
        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.send_message(message)
        return jsonify({'message': 'Password reset link has been sent! Please check your email.'}), 200
    except Exception as e:
        # Simulate success (in production, configure a real email service)
        print(f"Simulated email sent: {reset_link}")
        return jsonify({'message': 'Password reset link has been sent! Please check your email (simulated).'}), 200

# Process password reset
#
# Assumptions:
# - The request contains JSON data with 'token' and 'newPassword' fields.
# - The token was previously generated and stored in the reset_tokens table.
#
# Preconditions:
# - The database must be initialized (init_db() called).
# - The request must be a POST request with a JSON body.
#
# Inputs:
# - JSON object with:
#   - token (str): The JWT token sent to the user for password reset.
#   - newPassword (str): The new password to set for the user.
#
# Outputs:
# - Success: Returns a JSON response with a 'message' field and HTTP status 200.
# - Failure:
#   - If token is invalid/expired: Returns {'error': 'Reset link is invalid or has expired!'}, HTTP 400.
#   - If token has expired: Returns {'error': 'Reset link has expired!'}, HTTP 400.
@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('newPassword')

    try:
        # Verify the JWT token
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        email = payload['email']

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM reset_tokens WHERE token = ? AND email = ?', (token, email))
            token_record = cursor.fetchone()

        if not token_record:
            return jsonify({'error': 'Reset link is invalid or has expired!'}), 400

        # Update the user's password with the new hashed password
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

# Route to render the login page
#
# Assumptions:
# - The login.html template exists in app/templates/.
#
# Preconditions:
# - The template_folder must be correctly set in the Flask app configuration.
#
# Inputs:
# - None
#
# Outputs:
# - Renders the login.html template.
@app.route('/login.html')
def login_page():
    return render_template('login.html')

# Route to render the register page
#
# Assumptions:
# - The register.html template exists in app/templates/.
#
# Preconditions:
# - The template_folder must be correctly set in the Flask app configuration.
#
# Inputs:
# - None
#
# Outputs:
# - Renders the register.html template.
@app.route('/register.html')
def register_page():
    return render_template('register.html')

# Route to render the forgot password page
#
# Assumptions:
# - The forgot-password.html template exists in app/templates/.
#
# Preconditions:
# - The template_folder must be correctly set in the Flask app configuration.
#
# Inputs:
# - None
#
# Outputs:
# - Renders the forgot-password.html template.
@app.route('/forgot-password.html')
def forgot_password_page():
    return render_template('forgot-password.html')

# Route to render the reset password page
#
# Assumptions:
# - The reset-password.html template exists in app/templates/.
#
# Preconditions:
# - The template_folder must be correctly set in the Flask app configuration.
#
# Inputs:
# - None
#
# Outputs:
# - Renders the reset-password.html template.
@app.route('/reset-password.html')
def reset_password_page():
    return render_template('reset-password.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)