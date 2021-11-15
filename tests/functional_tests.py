import os
from selenium import webdriver
import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class NewTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Chrome(
            executable_path=os.path.dirname(os.path.abspath(__file__)) + '\chromedriver.exe')

    def tearDown(self):
        self.browser.quit()

    def test_access_website(self):
        self.browser.get('http://localhost:8000')

        self.assertIn('Index', self.browser.title)

        WebDriverWait(self.browser, 5).until(lambda d: d.find_element(By.NAME, 'submit_code'))

        self.browser.find_element(By.NAME, 'submit_code')

        WebDriverWait(self.browser, 5).until(lambda d: d.find_element(By.NAME, 'submit_simulator'))

        self.browser.find_element(By.NAME, 'submit_simulator')


if __name__ == '__main__':
    unittest.main(warnings='ignore')
