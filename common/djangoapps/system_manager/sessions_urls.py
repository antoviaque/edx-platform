from django.conf.urls import include, patterns, url

urlpatterns = patterns('system_manager.session_views',
    url(r'/*$^', 'session_list'),
    url(r'^(?P<pk>[a-z0-9]+)$', 'session_detail'),
)
