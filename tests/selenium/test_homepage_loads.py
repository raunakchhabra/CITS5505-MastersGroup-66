import unittest
from multiprocessing import Process, set_start_method
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from app import create_app

localHost = "http://127.0.0.1:5000"

def run_flask():
    app = create_app()
    app.config['TESTING'] = True
    app.run(port=5000, use_reloader=False)

class TestHomepageLoads(unittest.TestCase):
    def setUp(self):
        set_start_method("fork", force=True)
        self.server = Process(target=run_flask)
        self.server.start()
        time.sleep(2)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    def tearDown(self):
        self.driver.quit()
        self.server.terminate()

    def test_homepage_title(self):
        self.driver.get(localHost)
        self.assertIn("Lingua Track", self.driver.title)

if __name__ == "__main__":
    unittest.main()