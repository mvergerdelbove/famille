from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import TemplateView
from password_reset.views import Recover
from postman.views import WriteView, ReplyView
from tastypie.api import Api

from famille import resources
from famille.forms import CustomAuthenticationForm
from famille.utils.mail import email_moderation


admin.autodiscover()
api = Api(api_name='v1')
api.register(resources.PrestataireResource())
api.register(resources.FamilleResource())
api.register(resources.FamillePlanningResource())
api.register(resources.PrestatairePlanningResource())
api.register(resources.ScheduleResource())
api.register(resources.WeekdayResource())


urlpatterns = patterns(
    '',
    url(r'^$', "famille.views.home", name="home"),
    url(r'^in', 'django.contrib.auth.views.login', {
        'authentication_form': CustomAuthenticationForm
    }, name='auth_login'),
    url(r'^out/$', 'django.contrib.auth.views.logout', {
        'next_page': '/',
        'extra_context': {'action': 'logged_out'}
    }, name='auth_logout'),
    url(r'^mon-compte/$', 'famille.views.account', name="account"),
    url(r'^mon-compte/parametres-avances/', "famille.views.advanced", name="advanced"),
    url(
        r'^mon-compte/changer-de-mot-de-passe/$', 'django.contrib.auth.views.password_change',
        {
            'password_change_form': PasswordChangeForm,
            'post_change_redirect': '/mon-compte/parametres-avances/?success',
            'template_name': 'account/password_change.html'
        }, name="password_change"
    ),
    url(r'^mon-compte/suppression/$', 'famille.views.delete_account', name="delete_account"),
    url(r'^profile/(?P<type>[a-z]+)/(?P<uid>\d+)/$', "famille.views.profile", name="profile"),
    url(r'^devenir-premium/$', "famille.views.premium", name="premium"),
    url(r'^devenir-premium/succes/$', "famille.views.premium_success", name="premium_success"),
    url(r'^devenir-premium/annuler/$', "famille.views.premium_cancel", name="premium_cancel"),
    url(r'^recherche/$', 'famille.views.search', name="search"),
    url(r'^register(?:/(?P<social>[a-zA-Z]+)/((?P<type>[a-zA-Z]+)))?/$', 'famille.views.register', name="register"),
    url(r'^favorite/$', 'famille.views.favorite', name="favorite"),
    url(r'^tout-sur-la-garde-denfants/$', 'famille.views.tools', name="tools"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^recover/$', Recover.as_view(
        search_fields=["email"], email_template_name="password_reset/recovery_email.html",
        email_subject_template_name="password_reset/recovery_email_subject.txt"
    ), name='password_reset_recover'),
    # api
    url(r'^contact-favorites/$', 'famille.views.contact_favorites', name="contact_favorites"),
    url(r'^plannings/$', 'famille.views.plannings', name="plannings"),
    url(r'^profile-pic/$', 'famille.views.profile_pic', name="profile_pic"),
    url(r'^submit-rating/(?P<type>[a-z]+)/(?P<uid>\d+)/$', "famille.views.submit_rating", name="submit_rating"),
    url(r'^autocomplete/', "famille.views.message_autocomplete", name="message_autocomplete"),
    url(r'^api/', include(api.urls)),

    # static pages
    url(
        r'^confirmation/$', TemplateView.as_view(template_name="confirmation.html"),
        name="confirmation"
    ),
    url(
        r'^espace-famille/$', TemplateView.as_view(template_name="espace/famille.html"),
        name="espace_famille"
    ),
    url(
        r'^espace-prestataire/$', TemplateView.as_view(template_name="espace/prestataire.html"),
        name="espace_prestataire"
    ),

    # plugin urls
    url(r'^grappelli/', include('grappelli.urls')),  # grappelli
    url(r'^tinymce/', include('tinymce.urls')),  # tinymce
    url('', include('social.apps.django_app.urls', namespace='social')),  # social auth
    url(r'^paypal/', include('paypal.standard.ipn.urls')),  # paypal
    url(r'', include('password_reset.urls')),  # password reset
    url(r'^messages/write/(?:(?P<recipients>[^/#]+)/)?$', WriteView.as_view(auto_moderators=email_moderation), name='postman_write'),
    url(r'^messages/reply/(?P<message_id>[\d]+)/$', ReplyView.as_view(auto_moderators=email_moderation), name='postman_reply'),
    url(r'^messages/', include('postman.urls')),  # postman
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
