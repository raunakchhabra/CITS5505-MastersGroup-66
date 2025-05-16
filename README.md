# CITS5505-MastersGroup-66

This is a project for **language learning**.  
**LinguaTrack** allows users to enroll in language courses, track progress, and share results.

---

## 🌟 Team

| Student ID   | Name            | GitHub Username   |
|--------------|-----------------|-------------------|
| 24114899     | Lulu Zhang      | Cynthia-zll       |
| 23914274     | Raunak Chhabra  | raunakchhabra     |
| 24172041     | Julie Lei       | Juliet-L          |
| 24144144     | Yao Qin         | 5km5km            |

---

## 🚀 Project Overview

**LinguaTrack** is a **Flask-based web application** designed for smart language learning.  
It enables:
- User registration, login, and secure authentication
- Course enrollment and progress tracking
- Sharing achievements and results
- A polished, modern frontend with dynamic features

---

## ⚙️ Setup Instructions

1. **Clone the repository:**  
   `git clone https://github.com/raunakchhabra/CITS5505-MastersGroup-66.git`

2. **Activate virtual environment:**  
   `source pyvenv/bin/activate`

3. **Install dependencies:**  
   `pip install -r requirements.txt`

4. **Set up environment variables:**
  
   - Copy the example environment file:  
     `cp .flaskenv.example .flaskenv`
  
   - Edit `.flaskenv` with your configuration:
     ```bash
     # Edit the file and replace with your actual values
     nano .flaskenv  # or use your preferred text editor
     ```
  
   - Key variables to update:
     - `SECRET_KEY`: Generate a secure key using `python -c "import secrets; print(secrets.token_hex(16))"`
     - `MAIL_USERNAME`: Your Gmail address for sending emails
     - `MAIL_PASSWORD`: Your Gmail app password (not regular password)
     - Database paths and other settings as needed

5. **Database migration:**
   ```bash
   # 1. Skip the problematic migration
   flask db stamp 78294d82a87b
   # 2. Apply the remaining migrations
   flask db upgrade head
   ```

6. **Run the application:**
   ```bash
   python3 run.py
   ```
   The application will automatically load environment variables from `.flaskenv`.

---

## 🏗️ Project Features

- User authentication (register, login, password reset)
- Upload and visualize learning data (CSV, JSON)
- Manage and track language learning progress
- Share achievements with others
- Modern, responsive UI using HTML, CSS, JavaScript
- Modular backend using Flask + SQLAlchemy

---

## 🛠️ Project Structure

| Folder / File         | Purpose                                    |
|-----------------------|-------------------------------------------|
| `/app`                | Main Flask application code               |
| `/app/routes`         | Route definitions                         |
| `/app/models.py`      | Database models (SQLAlchemy)              |
| `/app/forms.py`       | Flask-WTF forms                           |
| `/static`             | Static files: CSS, JS, images             |
| `/templates`          | HTML templates (Jinja2)                   |
| `requirements.txt`    | Python dependencies                       |
| `run.py`              | Main entry point to launch app            |

---

## ✅ Testing Strategy

This project uses a robust automated testing setup that follows best practices in web application development:

### 🔹 Unit Tests
- Isolated using **in-memory SQLite databases (`sqlite:///:memory:`)** via a custom `TestConfig`
- Each test creates a fresh database and drops it after completion
- Ensures real database interaction without persistence or side effects
- Covers key models (`User`, `Course`, `Progress`) and forms (`RegistrationForm`, etc.)

### 🔹 Selenium Tests
- UI tests implemented using **Selenium with Headless Chrome**
- Flask server is booted in a separate **multiprocessing process** to simulate live conditions
- Tests cover login, registration, dashboard, progress bar, and logout
- Clean `setUp()` and `tearDown()` logic ensures safe and repeatable browser testing

This approach ensures:
- ✅ High test coverage  
- ✅ Speed and isolation  
- ✅ Realistic simulation of application behavior
