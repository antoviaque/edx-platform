from django.conf import settings

from rest_framework import authentication, permissions, status

class ApiKeyHeaderPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        debug_enabled = settings.DEBUG
        permission_granted = False
        api_key = getattr(settings, "EDX_API_KEY", None)
        api_key_match = False
        if api_key is not None:
            print request.__dict__
            header_key = request.META['headers']['X-Edx-Api-Key']
            if header_key is not None and header_key == api_key:
                api_key_match = True

        # DEBUG MODE -- NO API KEY SHOULD BE PRESENT
        if  permission_granted is False and debug_enabled and api_key is None:
            permission_granted = True

        # RELEASE MODE -- API KEY MUST BE PRESENT
        if permission_granted is False and debug_enabled is False and api_key is not None and api_key_match:
            permission_granted = True

        return permission_granted
