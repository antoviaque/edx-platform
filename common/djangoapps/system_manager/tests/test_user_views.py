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
        self.TEST_FIRST_NAME = str(uuid.uuid4())
        self.TEST_LAST_NAME = str(uuid.uuid4())
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


    """
    USER MAIN VIEWS
    """
    def test_user_list_post(self):
        test_uri = '/api/users'
        local_username = self.TEST_USERNAME + str(randint(11,99))
        data = {'email':self.TEST_EMAIL, 'username':local_username, 'password':self.TEST_PASSWORD, 'first_name': self.TEST_FIRST_NAME, 'last_name': self.TEST_LAST_NAME}
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.data['id'])
        self.assertGreater(response.data['id'], 0)
        self.assertGreater(len(response.data['uri']), 0)
        confirm_uri = test_uri + '/' + str(response.data['id'])
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertIsNotNone(response.data['email'])
        self.assertGreater(len(response.data['email']), 0)
        self.assertEqual(response.data['email'], self.TEST_EMAIL)
        self.assertIsNotNone(response.data['username'])
        self.assertGreater(len(response.data['username']), 0)
        self.assertEqual(response.data['username'], local_username)
        self.assertIsNotNone(response.data['first_name'])
        self.assertGreater(len(response.data['first_name']), 0)
        self.assertEqual(response.data['first_name'], self.TEST_FIRST_NAME)
        self.assertIsNotNone(response.data['last_name'])
        self.assertGreater(len(response.data['last_name']), 0)
        self.assertEqual(response.data['last_name'], self.TEST_LAST_NAME)


    def test_user_list_post_duplicate(self):
        test_uri = '/api/users'
        local_username = self.TEST_USERNAME + str(randint(11,99))
        data = {'email':self.TEST_EMAIL, 'username':local_username, 'password':self.TEST_PASSWORD, 'first_name': self.TEST_FIRST_NAME, 'last_name': self.TEST_LAST_NAME}
        response = self.do_post(test_uri, data)
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 409)
        self.assertIsNotNone(response.data['id'])
        self.assertGreater(response.data['id'], 0)
        self.assertGreater(len(response.data['uri']), 0)
        confirm_uri = test_uri + '/' + str(response.data['id'])
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertIsNotNone(response.data['email'])
        self.assertGreater(len(response.data['email']), 0)
        self.assertEqual(response.data['email'], self.TEST_EMAIL)
        self.assertIsNotNone(response.data['username'])
        self.assertGreater(len(response.data['username']), 0)
        self.assertEqual(response.data['username'], local_username)
        self.assertIsNotNone(response.data['message'])
        self.assertGreater(response.data['message'], 0)
        self.assertIsNotNone(response.data['field_conflict'])
        self.assertGreater(response.data['field_conflict'], 0)
        self.assertEqual(response.data['field_conflict'], 'username')


    def test_user_detail_get(self):
        test_uri = '/api/users'
        local_username = self.TEST_USERNAME + str(randint(11,99))
        data = {'email':self.TEST_EMAIL, 'username':local_username, 'password':self.TEST_PASSWORD, 'first_name': self.TEST_FIRST_NAME, 'last_name': self.TEST_LAST_NAME}
        response = self.do_post(test_uri, data)
        test_uri = test_uri + '/' + str(response.data['id'])
        response = self.do_get(test_uri)
        response_json = json.dumps(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['id'])
        self.assertGreater(response.data['id'], 0)
        self.assertIsNotNone(response.data['uri'])
        self.assertGreater(len(response.data['uri']), 0)
        self.assertEqual(response.data['uri'], test_uri)
        self.assertIsNotNone(response.data['email'])
        self.assertGreater(len(response.data['email']), 0)
        self.assertEqual(response.data['email'], self.TEST_EMAIL)
        self.assertIsNotNone(response.data['username'])
        self.assertGreater(len(response.data['username']), 0)
        self.assertEqual(response.data['username'], local_username)
        self.assertIsNotNone(response.data['first_name'])
        self.assertGreater(len(response.data['first_name']), 0)
        self.assertEqual(response.data['first_name'], self.TEST_FIRST_NAME)
        self.assertIsNotNone(response.data['last_name'])
        self.assertGreater(len(response.data['last_name']), 0)
        self.assertEqual(response.data['last_name'], self.TEST_LAST_NAME)


    def test_user_detail_delete(self):
        test_uri = '/api/users'
        local_username = self.TEST_USERNAME + str(randint(11,99))
        data = {'email':self.TEST_EMAIL, 'username':local_username, 'password':self.TEST_PASSWORD, 'first_name': self.TEST_FIRST_NAME, 'last_name': self.TEST_LAST_NAME}
        response = self.do_post(test_uri, data)
        test_uri = test_uri + '/' + str(response.data['id'])
        response = self.do_delete(test_uri)
        self.assertEqual(response.status_code, 204)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_user_detail_get_undefined(self):
        test_uri = '/api/users/123456789'
        response = self.do_get(test_uri)
        response_json = json.dumps(response.data)
        self.assertEqual(response.status_code, 404)


    """
    USER-GROUP RELATIONSHIPS
    """
    def test_user_groups_list_post(self):
        test_uri = '/api/groups'
        data = {'name': 'Alpha Group'}
        response = self.do_post(test_uri, data)
        group_id = response.data['id']
        test_uri = '/api/users'
        local_username = self.TEST_USERNAME + str(randint(11,99))
        data = {'email':self.TEST_EMAIL, 'username':local_username, 'password':self.TEST_PASSWORD, 'first_name': self.TEST_FIRST_NAME, 'last_name': self.TEST_LAST_NAME}
        response = self.do_post(test_uri, data)
        test_uri = test_uri + '/' + str(response.data['id'])
        response = self.do_get(test_uri)
        test_uri = test_uri + '/groups'
        data = { 'group_id': group_id }
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        self.assertGreater(len(response.data['uri']), 0)
        confirm_uri = test_uri + '/' + str(response.data['group_id'])
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertIsNotNone(response.data['group_id'])
        self.assertGreater(response.data['group_id'], 0)
        self.assertIsNotNone(response.data['user_id'])
        self.assertGreater(response.data['user_id'], 0)

    def test_user_groups_detail_get(self):
        test_uri = '/api/groups'
        data = {'name': 'Alpha Group'}
        response = self.do_post(test_uri, data)
        group_id = response.data['id']
        test_uri = '/api/users'
        local_username = self.TEST_USERNAME + str(randint(11,99))
        data = {'email':self.TEST_EMAIL, 'username':local_username, 'password':self.TEST_PASSWORD, 'first_name': self.TEST_FIRST_NAME, 'last_name': self.TEST_LAST_NAME}
        response = self.do_post(test_uri, data)
        user_id = response.data['id']
        test_uri = test_uri + '/' + str(response.data['id']) + '/groups'
        data = { 'group_id': group_id }
        response = self.do_post(test_uri, data)
        test_uri = test_uri + '/' + str(group_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['uri']), 0)
        self.assertEqual(response.data['uri'], test_uri)
        self.assertIsNotNone(response.data['group_id'])
        self.assertGreater(response.data['group_id'], 0)
        self.assertEqual(response.data['group_id'], str(group_id))
        self.assertIsNotNone(response.data['user_id'])
        self.assertGreater(response.data['user_id'], 0)
        self.assertEqual(response.data['user_id'], user_id)

    def test_user_groups_detail_delete(self):
        test_uri = '/api/groups'
        data = {'name': 'Alpha Group'}
        response = self.do_post(test_uri, data)
        group_id = response.data['id']
        test_uri = '/api/users'
        local_username = self.TEST_USERNAME + str(randint(11,99))
        data = {'email':self.TEST_EMAIL, 'username':local_username, 'password':self.TEST_PASSWORD, 'first_name': self.TEST_FIRST_NAME, 'last_name': self.TEST_LAST_NAME}
        response = self.do_post(test_uri, data)
        user_id = response.data['id']
        test_uri = test_uri + '/' + str(response.data['id']) + '/groups'
        data = { 'group_id': group_id }
        response = self.do_post(test_uri, data)
        test_uri = test_uri + '/' + str(group_id)
        response = self.do_delete(test_uri)
        self.assertEqual(response.status_code, 204)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_user_groups_detail_get_undefined(self):
        test_uri = '/api/groups'
        data = {'name': 'Alpha Group'}
        response = self.do_post(test_uri, data)
        group_id = response.data['id']
        test_uri = '/api/users'
        local_username = self.TEST_USERNAME + str(randint(11,99))
        data = {'email':self.TEST_EMAIL, 'username':local_username, 'password':self.TEST_PASSWORD, 'first_name': self.TEST_FIRST_NAME, 'last_name': self.TEST_LAST_NAME}
        response = self.do_post(test_uri, data)
        user_id = response.data['id']
        test_uri = '/api/users/' + str(user_id) + '/groups/' + str(group_id)
        response = self.do_get(test_uri)
        response_json = json.dumps(response.data)
        self.assertEqual(response.status_code, 404)
