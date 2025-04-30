from flask import Blueprint, render_template

# Create a blueprint for course-related routes
courses_bp = Blueprint('courses', __name__)

# Route to render the course list page with dummy data
@courses_bp.route('/courses')
def courses():
    dummy_courses = [
        {
            "name": "Beginner French",
            "level": "A1",
            "description": "Master the foundations of French grammar and conversation."
        },
        {
            "name": "Intermediate Japanese",
            "level": "B1",
            "description": "Enhance your vocabulary and fluency with daily practice."
        },
        {
            "name": "Spanish for Travelers",
            "level": "A2",
            "description": "Learn essential Spanish phrases and cultural etiquette."
        },
        {
            "name": "Business English",
            "level": "B2",
            "description": "Communicate effectively in professional English contexts."
        }
    ]
    return render_template("courses.html", courses=dummy_courses)
