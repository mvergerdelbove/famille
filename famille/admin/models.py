from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from famille.admin import forms
from famille.models import Prestataire, Famille, DownloadableFile
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


class DownloadableFileAdmin(admin.ModelAdmin):
    model = DownloadableFile
    form = forms.DownloadableFileForm
    list_display = ('name', 'file_type')
    search_fields = ['name', 'description']


# registering onto the admin site
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, TinyMCEFlatPageAdmin)
admin.site.register(Famille, FamilleAdmin)
admin.site.register(Prestataire, PrestataireAdmin)
admin.site.register(DownloadableFile, DownloadableFileAdmin)

# TODO:
#       - display photo on rows ?
#       - a way to display plannings ?
