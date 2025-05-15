import unittest
from app.models import User, Progress

class TestUserProgress(unittest.TestCase):
    def test_user_has_progress(self):
        user = User(name="Test", email="test@x.com", password_hash="xyz")
        progress = Progress(user=user)
        self.assertEqual(progress.user.email, "test@x.com")

if __name__ == "__main__":
    unittest.main()