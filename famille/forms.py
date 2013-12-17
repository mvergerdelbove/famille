from django.forms import ModelForm

from famille.models import Famille


class FamilleForm(ModelForm):
    class Meta:
        model = Famille
        exclude = ['created_at', 'updated_at', ]
