"""
Run these tests @ Devstack:
    rake fasttest_lms[common/djangoapps/system_manager/tests/test_views.py]
"""
from random import randint
import simplejson as json
import uuid

from django.core.cache import cache
from django.test import TestCase, Client
from django.test.utils import override_settings

from system_manager.tests.factories import (UserFactory, RegistrationFactory,
                                            UserProfileFactory,)

TEST_API_KEY = str(uuid.uuid4())

@override_settings(EDX_API_KEY=TEST_API_KEY)
class SystemApiTests(TestCase):

    def setUp(self):
        self.TEST_USERNAME = str(uuid.uuid4())
        self.TEST_PASSWORD = str(uuid.uuid4())
        self.TEST_EMAIL = str(uuid.uuid4()) + '@test.org'
        self.TEST_GROUP_NAME = str(uuid.uuid4())

        self.client = Client()
        cache.clear()

    def do_post(self, uri, data):
        json_data = json.dumps(data)
        headers = {
            'Content-Type':'application/json',
            'Content-Length':len(json_data),
            'X-Edx-Api-Key':str(TEST_API_KEY),
            }
        response = self.client.post(uri, headers=headers, data=data)
        return response

    def do_get(self, uri):
        headers = {
            'Content-Type':'application/json',
            'X-Edx-Api-Key':str(TEST_API_KEY),
            }
        response = self.client.get(uri, headers=headers)
        return response

    def do_delete(self, uri):
        headers = {
            'Content-Type':'application/json',
            'X-Edx-Api-Key':str(TEST_API_KEY),
            }
        response = self.client.delete(uri, headers=headers)
        return response


    def test_session_list_post(self):
        test_uri = '/api/users'
        local_username = self.TEST_USERNAME + str(randint(11,99))
        local_username = local_username[3:-1] # username is a 32-character field
        data = {'email':self.TEST_EMAIL, 'username':local_username, 'password':self.TEST_PASSWORD}
        response = self.do_post(test_uri, data)
        test_uri = '/api/sessions'
        data = {'username': local_username, 'password': self.TEST_PASSWORD }
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.data['token'])
        self.assertGreater(len(response.data['token']), 0)
        self.assertIsNotNone(response.data['uri'])
        self.assertGreater(len(response.data['uri']), 0)
        confirm_uri = test_uri + '/' + response.data['token']
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertIsNotNone(response.data['expires'])
        self.assertGreater(response.data['expires'], 0)
        self.assertIsNotNone(response.data['user'])
        self.assertGreater(len(response.data['user']), 0)
        self.assertIsNotNone(response.data['user']['username'])
        self.assertEqual(str(response.data['user']['username']), local_username)

    def test_session_detail_get(self):
        test_uri = '/api/users'
        local_username = self.TEST_USERNAME + str(randint(11,99))
        local_username = local_username[3:-1] # username is a 32-character field
        data = {'email':self.TEST_EMAIL, 'username':local_username, 'password':self.TEST_PASSWORD}
        response = self.do_post(test_uri, data)
        test_uri = '/api/sessions'
        data = {'username': local_username, 'password': self.TEST_PASSWORD }
        response = self.do_post(test_uri, data)
        test_uri = '/api/sessions' + '/' + response.data['token']
        response = self.do_get(test_uri)
        response_json = json.dumps(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['token'])
        self.assertGreater(len(response.data['token']), 0)
        self.assertIsNotNone(response.data['uri'])
        self.assertGreater(len(response.data['uri']), 0)
        self.assertEqual(response.data['uri'], test_uri)
        self.assertIsNotNone(response.data['expires'])
        self.assertGreater(response.data['expires'], 0)

    def test_session_detail_get_undefined(self):
        test_uri = '/api/sessions/123456789'
        response = self.do_get(test_uri)
        response_json = json.dumps(response.data)
        self.assertEqual(response.status_code, 404)
