import unittest
from multiprocessing import Process, set_start_method
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

localHost = "http://127.0.0.1:5000"

def run_flask():
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        test_user = User(name="Test User", email="test@example.com", password_hash=generate_password_hash("pass123"))
        db.session.add(test_user)
        db.session.commit()
    app.run(port=5000, use_reloader=False)

class TestValidLogin(unittest.TestCase):
    def setUp(self):
        set_start_method("fork", force=True)
        self.server = Process(target=run_flask)
        self.server.start()
        time.sleep(3)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    def tearDown(self):
        self.driver.quit()
        self.server.terminate()

    def test_login_redirects_to_dashboard(self):
        self.driver.get(localHost + "/login")
        self.driver.find_element(By.NAME, "email").send_keys("test@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("pass123")
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(2)
        self.assertIn("/dashboard", self.driver.current_url)

if __name__ == "__main__":
    unittest.main()