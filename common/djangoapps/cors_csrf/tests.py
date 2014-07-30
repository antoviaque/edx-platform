"""
Tests for the CORS CSRF middleware
"""

from mock import patch, Mock

from django.test import TestCase
from django.test.utils import override_settings
from django.middleware.csrf import CsrfViewMiddleware

from cors_csrf.middleware import CorsCSRFMiddleware


class Sentinel():
    """
    Sentinel object to test return values
    """
    pass


SENTINEL = Sentinel()


class TestCorsMiddlewareProcessRequest(TestCase):
    """
    Test processing a request through the middleware
    """
    def get_request(self, is_secure, http_referer):
        """
        Build a test request
        """
        request = Mock()
        request.META = {'HTTP_REFERER': http_referer}
        request.is_secure = lambda: is_secure
        return request

    def setUp(self):
        self.middleware = CorsCSRFMiddleware()

    def check_not_enabled(self, request):
        """
        Check that the middleware does NOT process the provided request
        """
        with patch.object(CsrfViewMiddleware, 'process_view') as mock_method:
            res = self.middleware.process_view(request, None, None, None)

        self.assertIsNone(res)
        self.assertFalse(mock_method.called)

    def check_enabled(self, request):
        """
        Check that the middleware does process the provided request
        """
        def cb_check_req_is_secure_false(request, callback, args, kwargs):
            """
            Check that the request doesn't pass (yet) the `is_secure()` test
            """
            self.assertFalse(request.is_secure())
            return SENTINEL

        with patch.object(CsrfViewMiddleware, 'process_view') as mock_method:
            mock_method.side_effect = cb_check_req_is_secure_false
            res = self.middleware.process_view(request, None, None, None)

        self.assertIs(res, SENTINEL)
        self.assertTrue(request.is_secure())

    def test_middleware(self):
        with override_settings(FEATURES={'ENABLE_CORS_HEADERS': True},
                               CORS_ORIGIN_WHITELIST=['foo.com']):
            request = self.get_request(is_secure=True,
                                       http_referer='https://foo.com/bar')
            self.check_enabled(request)

        with override_settings(FEATURES={'ENABLE_CORS_HEADERS': False},
                               CORS_ORIGIN_WHITELIST=['foo.com']):
            request = self.get_request(is_secure=True,
                                       http_referer='https://foo.com/bar')
            self.check_not_enabled(request)

        with override_settings(FEATURES={'ENABLE_CORS_HEADERS': True},
                               CORS_ORIGIN_WHITELIST=['bar.com']):
            request = self.get_request(is_secure=True,
                                       http_referer='https://foo.com/bar')
            self.check_not_enabled(request)

        with override_settings(FEATURES={'ENABLE_CORS_HEADERS': True},
                               CORS_ORIGIN_WHITELIST=['foo.com']):
            request = self.get_request(is_secure=False,
                                       http_referer='https://foo.com/bar')
            self.check_not_enabled(request)

        with override_settings(FEATURES={'ENABLE_CORS_HEADERS': True},
                               CORS_ORIGIN_WHITELIST=['foo.com']):
            request = self.get_request(is_secure=True,
                                       http_referer='https://bar.com/bar')
            self.check_not_enabled(request)

        with override_settings(FEATURES={'ENABLE_CORS_HEADERS': True},
                               CORS_ORIGIN_WHITELIST=['foo.com']):
            request = self.get_request(is_secure=True,
                                       http_referer='http://foo.com/bar')
            self.check_not_enabled(request)
