from django.conf.urls import include, patterns, url

urlpatterns = patterns('system_manager.user_views',
    url(r'/*$^', 'user_list'),
    url(r'^(?P<user_id>[0-9]+)$', 'user_detail'),
    url(r'^(?P<user_id>[0-9]+)/groups/*$', 'user_groups_list'),
    url(r'^(?P<user_id>[0-9]+)/groups/(?P<group_id>[0-9]+)$', 'user_groups_detail'),
)
