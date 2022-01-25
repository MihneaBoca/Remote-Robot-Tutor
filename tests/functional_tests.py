import os
import time

from selenium import webdriver
import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
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

        self.browser.find_element(By.LINK_TEXT, 'Remote Robot Tutor')

        WebDriverWait(self.browser, 5).until(lambda d: d.find_element(By.ID, 'terminal'))

        terminal = self.browser.find_element(By.ID, 'terminal')

        self.assertEqual(terminal.get_attribute('placeholder'), 'Enter Your Code...')

        code_mirror_element = self.browser.find_element(By.CSS_SELECTOR, ".CodeMirror")
        self.browser.execute_script(
            "arguments[0].CodeMirror.setValue(arguments[1]);", code_mirror_element, "Forward 10")

        self.browser.find_element(By.ID, 'mac_address')

        select = Select(self.browser.find_element(By.ID, 'connection_type'))

        select.select_by_visible_text('USB')

        select.select_by_visible_text('Bluetooth')

        select.select_by_visible_text('WIFI')


if __name__ == '__main__':
    unittest.main(warnings='ignore')
