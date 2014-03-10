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

from system_manager.serializers import UserSerializer
from system_manager.permissions import ApiKeyHeaderPermission

"""
BASE API RESOURCES
"""

@api_view(['GET'])
@permission_classes((ApiKeyHeaderPermission,))
def version_detail(request, version_id):
    response_data = {}
    response_data['version_id'] = version_id
    response_data['date_published'] = timezone.now().isoformat()
    response_data['documentation'] = "http://docs.openedxapi.apiary.io/#get-%2Fapi%2Fsystem"
    response_data['uri'] = request.path
    response_data['resources'] = []
    response_data['resources'].append({'uri':'/api/system/v1/sessions'})
    response_data['resources'].append({'uri':'/api/system/v1/users'})
    response_data['resources'].append({'uri':'/api/system/v1/groups'})
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((ApiKeyHeaderPermission,))
def system_detail(request):
    response_data = {}
    if "system" in request.path:
        response_data['name'] = "Open edX System API"
        response_data['description'] = "System interface for managing groups, users, and sessions."
        response_data['documentation'] = "http://docs.openedxapi.apiary.io/#get-%2Fapi%2Fsystem"
        response_data['uri'] = request.path
        response_data['versions'] = []
        response_data['versions'].append({'uri':'/api/system/v1'})
    else:
        response_data['name'] = "Open edX API"
        response_data['description'] = "Machine interface for interactions with Open edX."
        response_data['documentation'] = "http://docs.openedxapi.apiary.io"
        response_data['uri'] = request.path
        response_data['resources'] = []
        response_data['resources'].append({'uri':'/api/system'})
    return Response(response_data, status=status.HTTP_200_OK)
