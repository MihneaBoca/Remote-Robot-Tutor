from django.db import IntegrityError
from django.test import TestCase
from django.urls import resolve

from RemoteRobot.views import index


class MainPageTest(TestCase):

    def test_index(self):
        found = resolve('/')
        self.assertEqual(found.func, index)
