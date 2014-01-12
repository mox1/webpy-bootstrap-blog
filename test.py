import os
os.environ['WEB_ENV'] = 'test'

import unittest

import web
from web.browser import AppBrowser

import app
import seed
import model as m

b = AppBrowser(app.app)


class AppTest(unittest.TestCase):
    def setUp(self):
        seed.init()
        # Add global setup here
        pass


class TestIntegration(AppTest):
    def test_index(self):
        b.open('/')
        self.assertEqual(200, b.status)


class TestUser(AppTest):
    def test_password_is_crypted(self):
        u = m.User.create(email='jzellman@gmail.com',
                          password='test123')
        self.assertIsNotNone(u.salt)
        self.assertIsNotNone(u.crypted_password)
        self.assertTrue(u.authenticate('test123'))
        self.assertFalse(u.authenticate('test1234'))

        u.update_fields(password='testy')
        self.assertIsNotNone(u.salt)
        self.assertIsNotNone(u.crypted_password)
        self.assertTrue(u.authenticate('testy'))
        self.assertFalse(u.authenticate('test123'))

if __name__ == '__main__':
    unittest.main()
