from django import forms

from famille.models import Famille


class SimpleSearchForm(forms.Form):
    postal_code = forms.CharField(label="Code postal")


class FamilleForm(forms.ModelForm):
    class Meta:
        model = Famille
        exclude = ['created_at', 'updated_at', ]
