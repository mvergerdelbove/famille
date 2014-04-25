from django import forms
from django.contrib.flatpages.admin import FlatpageForm
from django.contrib.flatpages.models import FlatPage
from tinymce.widgets import TinyMCE

from famille.models import Famille, Prestataire


class TinyMCEForm(FlatpageForm):
    class Meta:
        model = FlatPage
        widgets = {
            'content': TinyMCE(attrs={'cols': 100, 'rows': 30}, content_language="fr")
        }


class UserForm(forms.ModelForm):
    class Meta:
        widgets = {
            "description": forms.Textarea()
        }

class FamilleForm(forms.ModelForm):
    class Meta(UserForm.Meta):
        model = Famille


class PrestataireForm(forms.ModelForm):
    class Meta(UserForm.Meta):
        model = Prestataire
