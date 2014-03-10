from django.conf import settings
from django.contrib.auth import authenticate, get_user, login, logout
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, load_backend
from django.contrib.auth.models import AnonymousUser, User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.utils.importlib import import_module
from django.utils import timezone

from rest_framework import authentication, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from system_manager.permissions import ApiKeyHeaderPermission
from system_manager.serializers import UserSerializer


"""
USER RESOURCES
"""

@api_view(['POST'])
@permission_classes((ApiKeyHeaderPermission,))
def user_list(request):
    """
    POST creates a new user in the system
    """
    print '******* in user_list *****'
    if request.method == 'POST':
        response_data = {}
        email = request.DATA['email']
        username = request.DATA['username']
        password = request.DATA['password']
        first_name = request.DATA.get('first_name', '')
        last_name = request.DATA.get('last_name', '')
        try:
            new_user = User.objects.create(email=email,  username=username)
            new_user.set_password(password)
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.save()
            response_data['email'] = new_user.email
            response_data['username'] = new_user.username
            response_data['first_name'] = new_user.first_name
            response_data['last_name'] = new_user.last_name
            response_data['id'] = new_user.id
            response_data['uri'] = request.path + '/' + str(new_user.id)
            return Response(response_data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            existing_user = User.objects.get(username=username)
            response_data['email'] = existing_user.email
            response_data['username'] = existing_user.username
            response_data['first_name'] = existing_user.first_name
            response_data['last_name'] = existing_user.last_name
            response_data['id'] = existing_user.id
            response_data['uri'] = request.path + '/' + str(existing_user.id)
            response_data['message'] = "User '%s' already exists." % existing_user.username
            response_data['field_conflict'] = 'username'
            return Response(response_data, status=status.HTTP_409_CONFLICT)
        except:
            return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(['GET','DELETE'])
@permission_classes((ApiKeyHeaderPermission,))
def user_detail(request, user_id):
    """
    GET retrieves an existing user from the system
    DELETE removes/inactivates/etc. an existing user
    """
    if request.method == 'GET':
        response_data = {}
        try:
            existing_user = User.objects.get(id=user_id, is_active=True)
            response_data['email'] = existing_user.email
            response_data['username'] = existing_user.username
            response_data['first_name'] = existing_user.first_name
            response_data['last_name'] = existing_user.last_name
            response_data['id'] = existing_user.id
            response_data['uri'] = request.path
            response_data['resources'] = []
            resource_uri = '/api/system/v1/users/%s/groups' % user_id
            response_data['resources'].append({'uri':resource_uri})
            return Response(response_data, status=status.HTTP_200_OK)
        except:
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'DELETE':
        response_data = {}
        try:
            existing_user = User.objects.get(id=user_id, is_active=True)
            existing_user.is_active = False
            existing_user.save()
        except:
            # It's ok if we don't find a match
            pass
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes((ApiKeyHeaderPermission,))
def user_groups_list(request, user_id):
    """
    POST creates a new user-group relationship in the system
    """
    if request.method == 'POST':
        response_data = {}
        user_id = user_id
        group_id = request.DATA['group_id']
        try:
            existing_user = User.objects.get(id=user_id)
            existing_user.groups.add(group_id)
            response_data['uri'] = request.path + '/' + str(group_id)
            response_data['user_id'] = str(user_id)
            response_data['group_id'] = str(group_id)
            return Response(response_data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            response_data['uri'] = request.path + '/' + str(group_id)
            response_data['message'] = "Relationship already exists."
            return Response(response_data, status=status.HTTP_409_CONFLICT)
        except:
            return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

@api_view(['GET','DELETE'])
@permission_classes((ApiKeyHeaderPermission,))
def user_groups_detail(request, user_id, group_id):
    """
    GET retrieves an existing user-group relationship from the system
    DELETE removes/inactivates/etc. an existing user-group relationship
    """
    if request.method == 'GET':
        response_data = {}
        try:
            existing_user = User.objects.get(id=user_id, is_active=True)
            existing_relationship = existing_user.groups.get(id=group_id)
            response_data['user_id'] = existing_user.id
            response_data['group_id'] = group_id
            response_data['uri'] = request.path
            return Response(response_data, status=status.HTTP_200_OK)
        except:
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'DELETE':
        response_data = {}
        try:
            existing_user = User.objects.get(id=user_id, is_active=True)
            existing_user.groups.remove(group_id)
            existing_user.save()
        except:
            # It's ok if we don't find a match
            pass
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)
