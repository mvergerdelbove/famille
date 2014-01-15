from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from tastypie.api import Api

from famille import resources


admin.autodiscover()
api = Api(api_name='v1')
api.register(resources.PrestataireResource())


urlpatterns = patterns(
    '',
    url(r'^$', "famille.views.home", name="home"),
    url(r'^in/$', 'django.contrib.auth.views.login', name='auth_login'),
    url(r'^out/$', 'django.contrib.auth.views.logout', {
        'next_page': '/',
        'extra_context': {'action': 'logged_out'}
    }, name='auth_logout'),
    url(r'^mon-compte/$', 'famille.views.account', name="account"),
    url(r'^register/$', 'famille.views.register', name="register"),
    url(
        r'^confirmation/$', TemplateView.as_view(template_name="confirmation.html"),
        name="confirmation"
    ),
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(api.urls)),
)
