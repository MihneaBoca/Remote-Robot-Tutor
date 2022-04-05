from django.db import IntegrityError
from django.test import TestCase
from django.urls import resolve, reverse

from RemoteRobot.views import index, simulator, short, traverse
from RemoteRobot.models import Code


class MainPageTest(TestCase):

    def test_index(self):
        found = resolve('/')
        self.assertEqual(found.func, index)

    def test_correct_index(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'index.html')

    def test_simulator(self):
        found = resolve('/simulator/')
        self.assertEqual(found.func, simulator)

    def test_correct_simulator(self):
        response = self.client.get('/simulator/')
        self.assertTemplateUsed(response, 'simulator.html')

    def test_short(self):
        found = resolve('/short/')
        self.assertEqual(found.func, short)

    def test_correct_short(self):
        response = self.client.get('/short/')
        self.assertTemplateUsed(response, 'short.html')

    def test_traverse(self):
        found = resolve('/traverse/')
        self.assertEqual(found.func, traverse)

    def test_correct_traverse(self):
        response = self.client.get('/traverse/')
        self.assertTemplateUsed(response, 'traverse.html')

    def test_can_save_to_database(self):
        user1 = Code(password='bird-rain-orange')
        user2 = Code(password='blue-camp-book')
        user1.save()
        user2.save()
        self.assertEqual('bird-rain-orange', Code.objects.get(password='bird-rain-orange').password)
        user1.delete()
        user2.delete()

    def test_unique_passcode(self):
        Code(password='bird-rain-orange').save()
        with self.assertRaises(Exception) as raised:
            Code(password='bird-rain-orange').save()
        self.assertEqual(IntegrityError, type(raised.exception))

    def test_can_use_same_code(self):
        user1 = Code(password='bird-rain-orange', code='f')
        user2 = Code(password='blue-camp-book', code='f')
        user1.save()
        user2.save()
        self.assertEqual('f', Code.objects.get(password='bird-rain-orange').code)
        self.assertEqual('f', Code.objects.get(password='blue-camp-book').code)
        user1.delete()
        user2.delete()

    def test_link_from_short(self):
        short_url = reverse("short")
        response = self.client.get(short_url)
        simulator_url = reverse("simulator")
        self.assertContains(
            response, 'href="{0}"'.format(simulator_url)
        )

    def test_link_from_traverse(self):
        traverse_url = reverse("traverse")
        response = self.client.get(traverse_url)
        simulator_url = reverse("simulator")
        self.assertContains(
            response, 'href="{0}"'.format(simulator_url)
        )

    def test_navigate(self):
        index_url = reverse("index")
        response = self.client.get(index_url)
        simulator_url = reverse("simulator")
        self.assertContains(
            response, 'href="{0}"'.format(simulator_url)
        )
        home_url = reverse("index")
        self.assertContains(
            response, 'href="{0}"'.format(home_url)
        )

