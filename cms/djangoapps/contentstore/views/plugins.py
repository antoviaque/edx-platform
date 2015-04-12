from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.utils.translation import ugettext as _
from django_future.csrf import ensure_csrf_cookie

from contentstore.utils import reverse_course_url
from contentstore.views.component import ADVANCED_COMPONENT_TYPES
from edxmako.shortcuts import render_to_response
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore

from student.auth import has_course_author_access
from util.json_request import JsonResponse
from xmodule.modulestore.exceptions import ItemNotFoundError

__all__ = ['plugins_handler']


@login_required
@ensure_csrf_cookie
def plugins_handler(request, course_key_string=None):
    course_key = CourseKey.from_string(course_key_string)
    if not has_course_author_access(request.user, course_key):
        raise PermissionDenied()

    response_format = request.REQUEST.get('format', 'html')
    if response_format == 'json' or 'application/json' in request.META.get('HTTP_ACCEPT', 'application/json'):
        if request.method == 'GET':
            raise NotImplementedError
        elif request.method == 'POST':
            raise NotImplementedError
        else:
            return HttpResponseBadRequest()
    elif response_format == 'html':
        if request.method != 'GET':
            return HttpResponseBadRequest()
        return _plugins_index(request, course_key)
    else:
        return HttpResponseNotFound()


def _plugins_index(request, course_key):
    try:
        course_module = modulestore().get_course(course_key)
    except ItemNotFoundError:
        return HttpResponseNotFound()

    return render_to_response('plugins_index.html', {
        'context_course': course_module,
        'available_plugins': ADVANCED_COMPONENT_TYPES,
        'plugins_callback_url': reverse_course_url('plugins_handler', course_key)
    })
