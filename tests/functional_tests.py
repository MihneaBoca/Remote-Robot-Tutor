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
        # Adam is a student who wants try out the Remote Robot Tutor app,
        # he goes on the website to have a look
        self.browser.get('http://localhost:8000')

        self.assertIn('Remote Robot Tutor', self.browser.title)

        WebDriverWait(self.browser, 5).until(lambda d: d.find_element(By.NAME, 'submit_code'))

        self.browser.find_element(By.NAME, 'submit_code')

        self.browser.find_element(By.LINK_TEXT, 'Remote Robot Tutor')

        WebDriverWait(self.browser, 5).until(lambda d: d.find_element(By.ID, 'terminal'))

        terminal = self.browser.find_element(By.ID, 'terminal')

        self.assertEqual(terminal.get_attribute('placeholder'), '/Enter Your Code...')

        # He tries to write in some code and writes the command 'Forward 10'
        code_mirror_element = self.browser.find_element(By.CSS_SELECTOR, ".CodeMirror")
        self.browser.execute_script(
            "arguments[0].CodeMirror.setValue(arguments[1]);", code_mirror_element, "Forward 10")

        self.browser.find_element(By.ID, 'password')

        self.browser.find_element(By.ID, 'id_submit_code')

        self.browser.find_element(By.ID, 'undo')

        self.browser.find_element(By.ID, 'disconnect')

        # He realises he dosn't have a robot so he decides to check out the simulator
        self.browser.find_element(By.LINK_TEXT, 'Simulator').click()

        self.browser.find_element(By.LINK_TEXT, 'Robot').click()

        self.browser.find_element(By.LINK_TEXT, 'Simulator').click()

        # He looks at the map displayed on the simulator and decides he wants to see a new one
        # and clicks on the New map button
        self.browser.find_element(By.ID, 'id_new_map').click()

        # After that he notices an option to add more red squares, he initially selects 0 then 4
        # and finally settles on 9 and generates a new map
        select = Select(self.browser.find_element(By.ID, 'red_squares'))

        select.select_by_visible_text('0')

        select.select_by_visible_text('4')

        select.select_by_visible_text('9')

        self.browser.find_element(By.ID, 'id_new_map').click()

        # He clicks the Run code button to see what happens but he doticies the sprite does not move
        self.browser.find_element(By.ID, 'id_submit_code').click()

        # He tries to give a command and tries 'Forward' and sees that this time the robot moves
        code_mirror_element = self.browser.find_element(By.CSS_SELECTOR, ".CodeMirror")
        self.browser.execute_script(
            "arguments[0].CodeMirror.setValue(arguments[1]);", code_mirror_element, "Forward")
        self.browser.find_element(By.ID, 'id_submit_code').click()

        # After the robot finishes its movement Adam clicks the Reset map button to reset the map
        self.browser.find_element(By.ID, 'reset_map').click()

        # He then tries the 'Backward' command
        code_mirror_element = self.browser.find_element(By.CSS_SELECTOR, ".CodeMirror")
        self.browser.execute_script(
            "arguments[0].CodeMirror.setValue(arguments[1]);", code_mirror_element, "Backward")
        self.browser.find_element(By.ID, 'id_submit_code').click()

        # Then he tries the 'TurnRight' command
        code_mirror_element = self.browser.find_element(By.CSS_SELECTOR, ".CodeMirror")
        self.browser.execute_script(
            "arguments[0].CodeMirror.setValue(arguments[1]);", code_mirror_element, "TurnRight")
        self.browser.find_element(By.ID, 'id_submit_code').click()

        # And just to be sure tries the 'TurnLeft' command
        code_mirror_element = self.browser.find_element(By.CSS_SELECTOR, ".CodeMirror")
        self.browser.execute_script(
            "arguments[0].CodeMirror.setValue(arguments[1]);", code_mirror_element, "TurnLeft")
        self.browser.find_element(By.ID, 'id_submit_code').click()

        # He also noticies there is a repeat command and there is an option for shorter commands
        # so he plays around with that
        code_mirror_element = self.browser.find_element(By.CSS_SELECTOR, ".CodeMirror")
        self.browser.execute_script(
            "arguments[0].CodeMirror.setValue(arguments[1]);", code_mirror_element, "w 3 r e")
        self.browser.find_element(By.ID, 'id_submit_code').click()

        # Having done that he notices there are a couple of challenges available to play with
        # and clicks on the traverse the map challenge
        self.browser.find_element(By.ID, 'traverse').click()

        # He has a look around then returns to the main simulator page with the Back button
        self.browser.find_element(By.ID, 'back').click()

        # Then he decides he wants to have a look at the shortest path challenge
        self.browser.find_element(By.ID, 'short').click()

        # After having played a bit with the simulator he returns back to the Robot page
        self.browser.find_element(By.LINK_TEXT, 'Robot').click()


if __name__ == '__main__':
    unittest.main(warnings='ignore')
