from django.test import TestCase, Client
import os
import pathlib
import unittest

from selenium import webdriver

from channels.testing import ChannelsLiveServerTestCase
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

# Create your tests here.
class MinesweeperTestCase(TestCase):
# Django and Client Testing
    def setUp(self):
        # create database objects here
        pass
    # get and test objects here
    def room_active_board_count(self):
        
        pass
    def test_index(self):
        # Set up client to make requests
        c = Client()

        # Send get request to index page and store response
        response = c.get("/")

        # Make sure status code is 200
        self.assertEqual(response.status_code, 200)

        # Make sure three flights are returned in the context
        self.assertEqual(response.context["flights"].count(), 3)

class WebpageTests(unittest.TestCase):

    def test_title(self):
        """Make sure title is correct"""
        driver.get(file_uri("counter.html"))
        self.assertEqual(driver.title, "Counter")

    def test_increase(self):
        """Make sure header updated to 1 after 1 click of increase button"""
        driver.get(file_uri("counter.html"))
        increase = driver.find_element_by_id("increase")
        increase.click()
        self.assertEqual(driver.find_element_by_tag_name("h1").text, "1")

    def test_decrease(self):
        """Make sure header updated to -1 after 1 click of decrease button"""
        driver.get(file_uri("counter.html"))
        decrease = driver.find_element_by_id("decrease")
        decrease.click()
        self.assertEqual(driver.find_element_by_tag_name("h1").text, "-1")

    def test_multiple_increase(self):
        """Make sure header updated to 3 after 3 clicks of increase button"""
        driver.get(file_uri("counter.html"))
        increase = driver.find_element_by_id("increase")
        for i in range(3):
            increase.click()


def file_uri(filename):
    return pathlib.Path(os.path.abspath(filename)).as_uri()
driver = webdriver.Chrome()



if __name__ == "__main__":
    unittest.main()