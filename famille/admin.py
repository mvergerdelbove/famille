# from django.contrib import admin
# from django.contrib.flatpages.models import FlatPage
# from django.contrib.flatpages.admin import (
#     FlatPageAdmin as OldFlatPageAdmin, FlatpageForm as OldFlatpageForm
# )
# from django import forms
# from redactor.widgets import RedactorEditor
# 
# 
# class FlatpageForm(OldFlatpageForm):
#     class Meta:
#         model = FlatPage
#         widgets = {
#            'content': RedactorEditor(),
#         }
# 
# class FlatPageAdmin(OldFlatPageAdmin):
#     form = FlatpageForm
# 
# 
# admin.site.unregister(FlatPage)
# admin.site.register(FlatPage, FlatPageAdmin)
