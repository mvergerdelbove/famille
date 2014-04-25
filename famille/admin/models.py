from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from .forms import TinyMCEForm
from famille.models import Prestataire, Famille
from famille.utils import admin_display


class TinyMCEFlatPageAdmin(FlatPageAdmin):
    form = TinyMCEForm


class FamilleAdmin(admin.ModelAdmin):
    model = Famille
    list_display = ('first_name', 'name', 'email', admin_display.pseudo_display, 'city', 'plan')
    search_fields = ['first_name', 'name', 'email']


class PrestataireAdmin(admin.ModelAdmin):
    model = Prestataire
    list_display = ('first_name', 'name', 'email', admin_display.pseudo_display, 'city', 'plan')
    search_fields = ['first_name', 'name', 'email']


# registering onto the admin site
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, TinyMCEFlatPageAdmin)
admin.site.register(Famille, FamilleAdmin)
admin.site.register(Prestataire, PrestataireAdmin)

# TODO: - exclude some fields
#       - display photo on rows ?
#       - desc to text area
#       - remove some fields : geolocations
#       - a way to display plannings ?
