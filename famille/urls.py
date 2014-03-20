from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from tastypie.api import Api

from famille import resources


admin.autodiscover()
api = Api(api_name='v1')
api.register(resources.PrestataireResource())
api.register(resources.FamilleResource())


urlpatterns = patterns(
    '',
    url(r'^$', "famille.views.home", name="home"),
    url(r'^in', 'django.contrib.auth.views.login', name='auth_login'),
    url(r'^out/$', 'django.contrib.auth.views.logout', {
        'next_page': '/',
        'extra_context': {'action': 'logged_out'}
    }, name='auth_logout'),
    url(r'^mon-compte/$', 'famille.views.account', name="account"),
    url(r'^mon-compte/visibilite/$', TemplateView.as_view(template_name="account/visibility.html"), name="visibility"),
    url(r'^mon-compte/stats/$', TemplateView.as_view(template_name="account/stats.html"), name="stats"),
    url(r'^profile/(?P<type>[a-z]+)/(?P<uid>\d+)/$', "famille.views.profile", name="profile"),
    url(r'^devenir-premium(?:/(?P<cancel>[a-zA-Z]+))?/$', "famille.views.premium", name="premium"),
    url(r'^recherche/$', 'famille.views.search', name="search"),
    url(r'^register(?:/(?P<social>[a-zA-Z]+)/((?P<type>[a-zA-Z]+)))?/$', 'famille.views.register', name="register"),
    url(r'^favorite/$', 'famille.views.favorite', name="favorite"),
    url(r'^contact-favorites/$', 'famille.views.contact_favorites', name="contact_favorites"),
    url(r'^plannings/$', 'famille.views.plannings', name="plannings"),
    url(r'^profile-pic/$', 'famille.views.profile_pic', name="profile_pic"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(api.urls)),

    # static pages
    url(
        r'^confirmation/$', TemplateView.as_view(template_name="confirmation.html"),
        name="confirmation"
    ),
    url(
        r'^espace-famille/$', TemplateView.as_view(template_name="espace_famille.html"),
        name="espace_famille"
    ),
    url(
        r'^espace-prestataire/$', TemplateView.as_view(template_name="espace_prestataire.html"),
        name="espace_prestataire"
    ),

    # plugin urls
    url(r'^grappelli/', include('grappelli.urls')),  # grappelli
    url(r'^tinymce/', include('tinymce.urls')),  # tinymce
    url('', include('social.apps.django_app.urls', namespace='social')),  # social auth
    url(r'^paypal/', include('paypal.standard.ipn.urls')),  # paypal
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
