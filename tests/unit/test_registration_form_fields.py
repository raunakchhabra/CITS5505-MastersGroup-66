import unittest
from app.forms import RegistrationForm

class TestRegistrationFormFields(unittest.TestCase):
    def test_email_field_label(self):
        form = RegistrationForm()
        self.assertEqual(form.email.label.text.lower(), "email")

if __name__ == "__main__":
    unittest.main()