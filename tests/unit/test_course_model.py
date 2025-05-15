import unittest
from app.models import Course, User

class TestCourseModel(unittest.TestCase):
    def test_course_teacher_relationship(self):
        teacher = User(name="Mr. Smith", email="smith@example.com", password_hash="abc")
        course = Course(name="English 101", teacher=teacher)
        self.assertEqual(course.teacher.name, "Mr. Smith")

if __name__ == "__main__":
    unittest.main()