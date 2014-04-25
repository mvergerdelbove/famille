from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from famille.admin import forms
from famille.models import Prestataire, Famille
from famille.utils import admin_display


class TinyMCEFlatPageAdmin(FlatPageAdmin):
    form = forms.TinyMCEForm


class FamilleAdmin(admin.ModelAdmin):
    model = Famille
    form = forms.FamilleForm
    list_display = ('first_name', 'name', 'email', admin_display.pseudo_display, 'city', 'plan')
    exclude = ('geolocation', 'user')
    search_fields = ['first_name', 'name', 'email']


class PrestataireAdmin(admin.ModelAdmin):
    model = Prestataire
    form = forms.PrestataireForm
    list_display = ('first_name', 'name', 'email', admin_display.pseudo_display, 'city', 'plan')
    exclude = ('geolocation', 'user')
    search_fields = ['first_name', 'name', 'email']


# registering onto the admin site
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, TinyMCEFlatPageAdmin)
admin.site.register(Famille, FamilleAdmin)
admin.site.register(Prestataire, PrestataireAdmin)

# TODO:
#       - display photo on rows ?
#       - a way to display plannings ?
