from django.conf.urls import include, patterns, url

"""
    The URI scheme for resources is as follows:
        Resource type: /api/{resource_type}
        Specific resource: /api/{resource_type}/{resource_id}

    The remaining URIs provide information about the API and/or module
        System: General context and intended usage
        API: Top-level description of overall API (must live somewhere)
"""

urlpatterns = patterns('system_manager.views',

    url(r'/*$^', 'system_detail'),
    url(r'/system$', 'system_detail'),
)




