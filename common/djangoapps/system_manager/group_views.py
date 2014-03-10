import uuid

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
from system_manager.models import GroupRelationship

"""
GROUP RESOURCES
"""

@api_view(['POST'])
@permission_classes((ApiKeyHeaderPermission,))
def group_list(request):
    """
    POST creates a new group in the system
    """
    if request.method == 'POST':
        response_data = {}
        original_group_name = request.DATA['name']
        try:
            # Group name must be unique, but we need to support dupes
            new_group = Group.objects.create(name=str(uuid.uuid4()))
            new_group.name = '{:04d}'.format(new_group.id) + ': ' + original_group_name
            new_group.record_active = True
            new_group.record_date_created = timezone.now()
            new_group.record_date_modified = timezone.now()
            new_group.save()
            # Relationship model also allows us to use duplicate names
            new_group_relationship = GroupRelationship.objects.create(name=original_group_name, group_id=new_group.id, parent_group_id='0')
            response_data['name'] = new_group_relationship.name
            response_data['id'] = new_group.id
            response_data['uri'] = request.path + '/' + str(new_group.id)
            return Response(response_data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            existing_group = Group.objects.get(name=original_group_name)
            response_data['name'] = existing_group.name
            response_data['id'] = existing_group.id
            response_data['uri'] = request.path + '/' + str(existing_group.id)
            response_data['message'] = "Group '%s' already exists." % existing_group.name
            response_data['field_conflict'] = 'name'
            return Response(response_data, status=status.HTTP_409_CONFLICT)
        except:
            return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(['GET','DELETE'])
@permission_classes((ApiKeyHeaderPermission,))
def group_detail(request, pk):
    """
    GET retrieves an existing group from the system
    DELETE removes/inactivates/etc. an existing group
    """
    if request.method == 'GET':
        response_data = {}
        try:
            existing_group = Group.objects.get(id=pk)
            existing_group_relationship = GroupRelationship.objects.get(group_id=pk)
            response_data['name'] = existing_group_relationship.name
            response_data['id'] = existing_group.id
            response_data['uri'] = request.path
            response_data['resources'] = []
            resource_uri = '/api/system/v1/groups/%s/users' % pk
            response_data['resources'].append({'uri':resource_uri})
            resource_uri = '/api/system/v1/groups/%s/groups' % pk
            response_data['resources'].append({'uri':resource_uri})
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception:
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'DELETE':
        return Response(None, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes((ApiKeyHeaderPermission,))
def group_users_list(request, group_id):
    """
    POST creates a new group-user relationship in the system
    """
    if request.method == 'POST':
        response_data = {}
        group_id = group_id
        user_id = request.DATA['user_id']
        try:
            existing_group = Group.objects.get(id=group_id)
            existing_group.user_set.add(user_id)
            response_data['uri'] = request.path + '/' + str(user_id)
            response_data['group_id'] = str(group_id)
            response_data['user_id'] = str(user_id)
            return Response(response_data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            response_data['uri'] = request.path + '/' + str(user_id)
            response_data['message'] = "Relationship already exists."
            return Response(response_data, status=status.HTTP_409_CONFLICT)
        except:
            return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

@api_view(['GET','DELETE'])
@permission_classes((ApiKeyHeaderPermission,))
def group_users_detail(request, group_id, user_id):
    """
    GET retrieves an existing group-user relationship from the system
    DELETE removes/inactivates/etc. an existing group-user relationship
    """
    if request.method == 'GET':
        response_data = {}
        try:
            existing_group = Group.objects.get(id=group_id)
            existing_relationship = existing_group.user_set.get(id=user_id)
            response_data['group_id'] = existing_group.id
            response_data['user_id'] = user_id
            response_data['uri'] = request.path
            return Response(response_data, status=status.HTTP_200_OK)
        except:
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'DELETE':
        response_data = {}
        try:
            existing_group = Group.objects.get(id=group_id)
            existing_group.user_set.remove(user_id)
            existing_group.save()
        except:
            # It's ok if we don't find a match
            pass
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes((ApiKeyHeaderPermission,))
def group_groups_list(request, group_id):
    """
    POST creates a new group-group relationship in the system
    """
    if request.method == 'POST':
        response_data = {}
        group_id = group_id
        to_group_id = request.DATA['group_id']
        relationship_type = request.DATA['relationship_type']
        try:
            from_group = Group.objects.get(id=group_id)
            from_group_relationship = GroupRelationship.objects.get(group=from_group)
            to_group = Group.objects.get(id=to_group_id)
            to_group_relationship = GroupRelationship.objects.get(group=to_group)
            if relationship_type == 'h':
                to_group_relationship.parent_group = from_group_relationship
                to_group_relationship.save()
            elif relationship_type == 'g':
                new_relationship = from_group_relationship.add_linked_group_relationship(to_group_relationship)
            else:
                response_data['message'] = "Relationship type '%s' not currently supported" % relationship_type
                response_data['field_conflict'] = 'relationship_type'
                return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)
            response_data['uri'] = request.path + '/' + str(to_group.id)
            response_data['group_id'] = str(to_group.id)
            response_data['relationship_type'] = relationship_type
            return Response(response_data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            response_data['uri'] = request.path + '/' + str(user_id)
            response_data['message'] = "Relationship already exists."
            return Response(response_data, status=status.HTTP_409_CONFLICT)
        except:
            return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

@api_view(['GET','DELETE'])
@permission_classes((ApiKeyHeaderPermission,))
def group_groups_detail(request, group_id, related_group_id):
    """
    GET retrieves an existing group-group relationship from the system
    DELETE removes/inactivates/etc. an existing group-group relationship
    """
    if request.method == 'GET':
        response_data = {}
        try:
            from_group = Group.objects.get(id=group_id)
            from_group_relationship = GroupRelationship.objects.get(group_id=from_group)
            to_group = Group.objects.get(id=related_group_id)
            to_group_relationship = GroupRelationship.objects.get(group_id=to_group)
            if to_group_relationship.parent_group_id is not from_group_relationship.group_id:
                linked_group_exists = from_group_relationship.check_linked_group_relationship(to_group_relationship)
                if linked_group_exists is False:
                    return Response(response_data, status=status.HTTP_404_NOT_FOUND)
                else:
                    response_data['relationship_type'] = 'g'
            else:
                response_data['relationship_type'] = 'h'
            response_data['group_id'] = to_group_relationship.group_id
            response_data['uri'] = request.path
            return Response(response_data, status=status.HTTP_200_OK)
        except:
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'DELETE':
        response_data = {}
        try:
            from_group = Group.objects.get(id=group_id)
            from_group_relationship = GroupRelationship.objects.get(group_id=from_group)
            to_group = Group.objects.get(id=related_group_id)
            to_group_relationship = GroupRelationship.objects.get(group_id=to_group)
            if to_group_relationship.parent_group_id is from_group_relationship.group_id:
                to_group_relationship.parent_group_id = None
                to_group_relationship.save()
            else:
                from_group_relationship.remove_linked_group_relationship(to_group_relationship)
                from_group_relationship.save()
                to_group_relationship.remove_linked_group_relationship(from_group_relationship)
                to_group_relationship.save()
            return Response(response_data, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
