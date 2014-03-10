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

        self.user = UserFactory.build(username=self.TEST_USERNAME, email=self.TEST_EMAIL)
        self.user.set_password(self.TEST_PASSWORD)
        self.user.save()

        RegistrationFactory(user=self.user)
        UserProfileFactory(user=self.user)

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


    def test_system_detail_get(self):
        test_uri = '/api/system'
        response = self.do_get(test_uri)
        response_json = json.dumps(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['uri'])
        self.assertGreater(len(response.data['uri']), 0)
        self.assertEqual(response.data['uri'], test_uri)
        self.assertIsNotNone(response.data['documentation'])
        self.assertGreater(len(response.data['documentation']), 0)
        self.assertIsNotNone(response.data['name'])
        self.assertGreater(len(response.data['name']), 0)
        self.assertIsNotNone(response.data['description'])
        self.assertGreater(len(response.data['description']), 0)


    def test_system_detail_api_get(self):
        test_uri = '/api'
        response = self.do_get(test_uri)
        response_json = json.dumps(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['uri'])
        self.assertGreater(len(response.data['uri']), 0)
        self.assertEqual(response.data['uri'], test_uri)
        self.assertIsNotNone(response.data['documentation'])
        self.assertGreater(len(response.data['documentation']), 0)
        self.assertIsNotNone(response.data['name'])
        self.assertGreater(len(response.data['name']), 0)
        self.assertIsNotNone(response.data['description'])
        self.assertGreater(len(response.data['description']), 0)
