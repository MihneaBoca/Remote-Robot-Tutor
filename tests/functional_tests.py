import os

from selenium import webdriver
import unittest
from webdriver_manager.chrome import ChromeDriverManager


class NewTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Chrome(executable_path=os.path.dirname(os.path.abspath(__file__)) + '\chromedriver.exe')

    def tearDown(self):
        self.browser.quit()

    def test_access_website(self):

        self.browser.get('http://localhost:8000')

        self.assertIn('Index', self.browser.title)


if __name__ == '__main__':
    unittest.main(warnings='ignore')
