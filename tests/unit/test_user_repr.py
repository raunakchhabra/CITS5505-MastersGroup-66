import unittest
from app.models import User

class TestUserRepr(unittest.TestCase):
    def test_user_string_output(self):
        user = User(name="Alice", email="alice@example.com", password_hash="x")
        self.assertIn("Alice", repr(user))

if __name__ == "__main__":
    unittest.main()