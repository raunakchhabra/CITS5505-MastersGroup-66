import unittest
from werkzeug.security import generate_password_hash, check_password_hash

class TestPasswordHashing(unittest.TestCase):
    def test_password_check(self):
        password = "TestPass123"
        hashed = generate_password_hash(password)
        self.assertTrue(check_password_hash(hashed, password))
        self.assertFalse(check_password_hash(hashed, "WrongPass"))

if __name__ == "__main__":
    unittest.main()