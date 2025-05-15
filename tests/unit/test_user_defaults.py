import unittest
from app.models import User

class TestUserDefaults(unittest.TestCase):
    def test_default_user_fields(self):
        user = User(name="Jane Doe", email="jane@example.com", password_hash="123")
        self.assertEqual(user.role, "student")
        self.assertEqual(user.xp, 0)
        self.assertEqual(user.streak_days, 0)

if __name__ == "__main__":
    unittest.main()