from selenium import webdriver

def test_dummy_ui():
    driver = webdriver.Chrome()
    driver.get("http://localhost:5000")  # Adjust the URL if needed

    assert "Your App Title" in driver.title

    driver.quit()
