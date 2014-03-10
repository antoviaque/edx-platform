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
        self.BASE_USERS_URI = '/api/users'
        self.BASE_GROUPS_URI = '/api/groups'

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


    def test_group_list_post(self):
        data = {'name': self.TEST_GROUP_NAME}
        response = self.do_post(self.BASE_GROUPS_URI, data)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.data['id'])
        self.assertGreater(response.data['id'], 0)
        self.assertGreater(len(response.data['uri']), 0)
        confirm_uri = self.BASE_GROUPS_URI + '/' + str(response.data['id'])
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertIsNotNone(response.data['name'])
        self.assertGreater(len(response.data['name']), 0)

    # def test_group_list_post_duplicate(self):
    #     data = {'name': self.TEST_GROUP_NAME}
    #     response = self.do_post(self.BASE_GROUPS_URI, data)
    #     response = self.do_post(self.BASE_GROUPS_URI, data)
    #     self.assertEqual(response.status_code, 409)
    #     self.assertIsNotNone(response.data['id'])
    #     self.assertGreater(response.data['id'], 0)
    #     self.assertGreater(len(response.data['uri']), 0)
    #     confirm_uri = self.BASE_GROUPS_URI + '/' + str(response.data['id'])
    #     self.assertEqual(response.data['uri'], confirm_uri)
    #     self.assertIsNotNone(response.data['name'])
    #     self.assertGreater(len(response.data['name']), 0)
    #     self.assertIsNotNone(response.data['message'])
    #     self.assertGreater(response.data['message'], 0)
    #     self.assertIsNotNone(response.data['field_conflict'])
    #     self.assertGreater(response.data['field_conflict'], 0)
    #     self.assertEqual(response.data['field_conflict'], 'name')

    def test_group_detail_get(self):
        data = {'name': self.TEST_GROUP_NAME}
        response = self.do_post(self.BASE_GROUPS_URI, data)
        test_uri = self.BASE_GROUPS_URI + '/' + str(response.data['id'])
        response = self.do_get(test_uri)
        response_json = json.dumps(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['id'])
        self.assertGreater(response.data['id'], 0)
        self.assertIsNotNone(response.data['uri'])
        self.assertGreater(len(response.data['uri']), 0)
        self.assertEqual(response.data['uri'], test_uri)
        self.assertIsNotNone(response.data['name'])
        self.assertGreater(len(response.data['name']), 0)

    def test_group_detail_get_undefined(self):
        test_uri = self.BASE_GROUPS_URI + '/123456789'
        response = self.do_get(test_uri)
        response_json = json.dumps(response.data)
        self.assertEqual(response.status_code, 404)

    """
    GROUP-USER RELATIONSHIPS
    """
    def test_group_users_list_post(self):
        local_username = self.TEST_USERNAME + str(randint(11,99))
        data = {'email':self.TEST_EMAIL, 'username':local_username, 'password':self.TEST_PASSWORD}
        response = self.do_post(self.BASE_USERS_URI, data)
        user_id = response.data['id']
        data = {'name': 'Alpha Group'}
        response = self.do_post(self.BASE_GROUPS_URI, data)
        test_uri = self.BASE_GROUPS_URI + '/' + str(response.data['id'])
        response = self.do_get(test_uri)
        test_uri = test_uri + '/users'
        data = { 'user_id': user_id }
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        self.assertGreater(len(response.data['uri']), 0)
        confirm_uri = test_uri + '/' + str(response.data['user_id'])
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertIsNotNone(response.data['group_id'])
        self.assertGreater(response.data['group_id'], 0)
        self.assertIsNotNone(response.data['user_id'])
        self.assertGreater(response.data['user_id'], 0)

    def test_group_users_detail_get(self):
        local_username = self.TEST_USERNAME + str(randint(11,99))
        data = {'email':self.TEST_EMAIL, 'username':local_username, 'password':self.TEST_PASSWORD}
        response = self.do_post(self.BASE_USERS_URI, data)
        user_id = response.data['id']
        data = {'name': 'Alpha Group'}
        response = self.do_post(self.BASE_GROUPS_URI, data)
        print response.data
        group_id = response.data['id']
        test_uri = self.BASE_GROUPS_URI + '/' + str(response.data['id'])
        response = self.do_get(test_uri)
        test_uri = test_uri + '/users'
        data = { 'user_id': user_id }
        response = self.do_post(test_uri, data)
        test_uri = test_uri + '/' + str(user_id)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['uri']), 0)
        self.assertEqual(response.data['uri'], test_uri)
        self.assertIsNotNone(response.data['group_id'])
        self.assertGreater(response.data['group_id'], 0)
        self.assertEqual(response.data['group_id'], group_id)
        self.assertIsNotNone(response.data['user_id'])
        self.assertGreater(response.data['user_id'], 0)
        self.assertEqual(response.data['user_id'], str(user_id))

    def test_group_users_detail_delete(self):
        local_username = self.TEST_USERNAME + str(randint(11,99))
        data = {'email':self.TEST_EMAIL, 'username':local_username, 'password':self.TEST_PASSWORD}
        response = self.do_post(self.BASE_USERS_URI, data)
        user_id = response.data['id']
        data = {'name': 'Alpha Group'}
        response = self.do_post(self.BASE_GROUPS_URI, data)
        test_uri = self.BASE_GROUPS_URI + '/' + str(response.data['id'])
        response = self.do_get(test_uri)
        test_uri = test_uri + '/users'
        data = { 'user_id': user_id }
        response = self.do_post(test_uri, data)
        test_uri = test_uri + '/' + str(user_id)
        response = self.do_delete(test_uri)
        self.assertEqual(response.status_code, 204)
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)

    def test_group_users_detail_get_undefined(self):
        local_username = self.TEST_USERNAME + str(randint(11,99))
        data = {'email':self.TEST_EMAIL, 'username':local_username, 'password':self.TEST_PASSWORD}
        response = self.do_post(self.BASE_USERS_URI, data)
        user_id = response.data['id']
        data = {'name': 'Alpha Group'}
        response = self.do_post(self.BASE_GROUPS_URI, data)
        group_id = response.data['id']
        test_uri = self.BASE_GROUPS_URI + '/' + str(group_id) + '/users/' + str(user_id)
        response = self.do_get(test_uri)
        response_json = json.dumps(response.data)
        self.assertEqual(response.status_code, 404)



    """
    GROUP-GROUP RELATIONSHIPS
    """
    def test_group_groups_list_post_hierarchical(self):
        data = {'name': 'Alpha Group'}
        alpha_response = self.do_post(self.BASE_GROUPS_URI, data)
        data = {'name': 'Beta Group'}
        beta_response = self.do_post(self.BASE_GROUPS_URI, data)
        data = {'name': 'Delta Group'}
        delta_response = self.do_post(self.BASE_GROUPS_URI, data)
        test_uri = alpha_response.data['uri'] + '/groups'
        group_id = delta_response.data['id']
        relationship_type = 'h' # Heirarchical
        data = { 'group_id': group_id, 'relationship_type': relationship_type }
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        self.assertGreater(len(response.data['uri']), 0)
        confirm_uri = test_uri + '/' + str(response.data['group_id'])
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertIsNotNone(response.data['group_id'])
        self.assertGreater(response.data['group_id'], 0)
        self.assertEqual(response.data['group_id'], str(group_id))
        self.assertIsNotNone(response.data['relationship_type'])
        self.assertGreater(len(response.data['relationship_type']), 0)
        self.assertEqual(response.data['relationship_type'], relationship_type)

    def test_group_groups_list_post_linked(self):
        data = {'name': 'Alpha Group'}
        alpha_response = self.do_post(self.BASE_GROUPS_URI, data)
        data = {'name': 'Beta Group'}
        beta_response = self.do_post(self.BASE_GROUPS_URI, data)
        data = {'name': 'Delta Group'}
        delta_response = self.do_post(self.BASE_GROUPS_URI, data)
        test_uri = alpha_response.data['uri'] + '/groups'
        group_id = delta_response.data['id']
        relationship_type = 'g' # Graph
        data = { 'group_id': group_id, 'relationship_type': relationship_type }
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        self.assertGreater(len(response.data['uri']), 0)
        confirm_uri = test_uri + '/' + str(response.data['group_id'])
        self.assertEqual(response.data['uri'], confirm_uri)
        self.assertIsNotNone(response.data['group_id'])
        self.assertGreater(response.data['group_id'], 0)
        self.assertEqual(response.data['group_id'], str(group_id))
        self.assertIsNotNone(response.data['relationship_type'])
        self.assertGreater(len(response.data['relationship_type']), 0)
        self.assertEqual(response.data['relationship_type'], relationship_type)

    def test_group_groups_detail_get_hierarchical(self):
        data = {'name': 'Alpha Group'}
        alpha_response = self.do_post(self.BASE_GROUPS_URI, data)
        data = {'name': 'Beta Group'}
        beta_response = self.do_post(self.BASE_GROUPS_URI, data)
        data = {'name': 'Delta Group'}
        delta_response = self.do_post(self.BASE_GROUPS_URI, data)
        test_uri = alpha_response.data['uri'] + '/groups'
        group_id = delta_response.data['id']
        relationship_type = 'h' # Hierarchical
        data = { 'group_id': group_id, 'relationship_type': relationship_type }
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        test_uri = response.data['uri']
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['uri']), 0)
        self.assertEqual(response.data['uri'], test_uri)
        self.assertIsNotNone(response.data['group_id'])
        self.assertGreater(response.data['group_id'], 0)
        self.assertEqual(response.data['group_id'], group_id)
        self.assertIsNotNone(response.data['relationship_type'])
        self.assertGreater(len(response.data['relationship_type']), 0)
        self.assertEqual(response.data['relationship_type'], relationship_type)

    def test_group_groups_detail_get_linked(self):
        data = {'name': 'Alpha Group'}
        alpha_response = self.do_post(self.BASE_GROUPS_URI, data)
        data = {'name': 'Beta Group'}
        beta_response = self.do_post(self.BASE_GROUPS_URI, data)
        data = {'name': 'Delta Group'}
        delta_response = self.do_post(self.BASE_GROUPS_URI, data)
        test_uri = alpha_response.data['uri'] + '/groups'
        group_id = delta_response.data['id']
        relationship_type = 'g' #Graph
        data = { 'group_id': group_id, 'relationship_type': relationship_type }
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        test_uri = response.data['uri']
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['uri']), 0)
        self.assertEqual(response.data['uri'], test_uri)
        self.assertIsNotNone(response.data['group_id'])
        self.assertGreater(response.data['group_id'], 0)
        self.assertEqual(response.data['group_id'], group_id)
        self.assertIsNotNone(response.data['relationship_type'])
        self.assertGreater(len(response.data['relationship_type']), 0)
        self.assertEqual(response.data['relationship_type'], relationship_type)

    def test_group_groups_detail_delete_hierarchical(self):
        data = {'name': 'Alpha Group'}
        alpha_response = self.do_post(self.BASE_GROUPS_URI, data)
        data = {'name': 'Beta Group'}
        beta_response = self.do_post(self.BASE_GROUPS_URI, data)
        data = {'name': 'Delta Group'}
        delta_response = self.do_post(self.BASE_GROUPS_URI, data)
        data = {'name': 'Gamma Group'}
        gamma_response = self.do_post(self.BASE_GROUPS_URI, data)
        test_uri = alpha_response.data['uri'] + '/groups'
        group_id = gamma_response.data['id']
        relationship_type = 'h'
        data = { 'group_id': group_id, 'relationship_type': relationship_type }
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        test_uri = response.data['uri']
        response = self.do_delete(test_uri)
        self.assertEqual(response.status_code, 204)
        try:
            self.assertIsNone(response.data['message'])
        except KeyError:
            pass
        print test_uri
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)


    def test_group_groups_detail_delete_linked(self):
        data = {'name': 'Alpha Group'}
        alpha_response = self.do_post(self.BASE_GROUPS_URI, data)
        data = {'name': 'Beta Group'}
        beta_response = self.do_post(self.BASE_GROUPS_URI, data)
        data = {'name': 'Delta Group'}
        delta_response = self.do_post(self.BASE_GROUPS_URI, data)
        data = {'name': 'Gamma Group'}
        gamma_response = self.do_post(self.BASE_GROUPS_URI, data)
        test_uri = alpha_response.data['uri'] + '/groups'
        group_id = gamma_response.data['id']
        relationship_type = 'g'
        data = { 'group_id': group_id, 'relationship_type': relationship_type }
        response = self.do_post(test_uri, data)
        self.assertEqual(response.status_code, 201)
        test_uri = response.data['uri']
        response = self.do_delete(test_uri)
        self.assertEqual(response.status_code, 204)
        try:
            self.assertIsNone(response.data['message'])
        except KeyError:
            pass
        print test_uri
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 404)
