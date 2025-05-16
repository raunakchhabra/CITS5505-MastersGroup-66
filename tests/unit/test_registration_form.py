import unittest
from app.forms import RegistrationForm

class TestRegistrationForm(unittest.TestCase):
    def test_form_has_fields(self):
        form = RegistrationForm()
        self.assertTrue(hasattr(form, "name"))
        self.assertTrue(hasattr(form, "email"))
        self.assertTrue(hasattr(form, "password"))
        self.assertTrue(hasattr(form, "confirm_password"))

    def test_password_match_validation(self):
        form = RegistrationForm(data={
            "name": "Test",
            "email": "test@test.com",
            "password": "abc123",
            "confirm_password": "abc123"
        })
        self.assertTrue(form.validate())

if __name__ == "__main__":
    unittest.main()