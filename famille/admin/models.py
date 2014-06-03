from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from famille.admin import forms
from famille.models import Prestataire, Famille, DownloadableFile
from famille.utils import admin_display


class TinyMCEFlatPageAdmin(FlatPageAdmin):
    form = forms.TinyMCEForm


class BaseUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'name', admin_display.pseudo_display, 'city', 'plan', 'is_active')
    list_display_links = ('email', )
    exclude = ('geolocation', 'user')
    search_fields = ['first_name', 'name', 'email']
    list_filter = ('newsletter', )

    def is_active(self, obj):
        img = '<img src="/static/admin/img/icon-%s.gif" alt="%s">'
        params = ("yes", "True") if obj.user.is_active else ("no", "False")
        return img % params
    is_active.short_description = 'Actif'
    is_active.allow_tags = True


class FamilleAdmin(BaseUserAdmin):
    model = Famille
    form = forms.FamilleForm


class PrestataireAdmin(BaseUserAdmin):
    model = Prestataire
    form = forms.PrestataireForm


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
