from django import forms
from django.contrib.auth.models import User

from famille.models import Famille, Prestataire


class RegistrationForm(forms.Form):
    email = forms.CharField(label="Adresse mail")
    password = forms.CharField(
        label="Mot de passe", widget=forms.PasswordInput
    )

    def is_valid(self):
        if not super(RegistrationForm, self).is_valid():
            return False

        user_exists = bool(User.objects.filter(username=self.cleaned_data["email"]).first())
        return not user_exists

    def save(self):
        # Create user
        dj_user = User.objects.create_user(
            self.cleaned_data["email"],
            self.cleaned_data["email"],
            self.cleaned_data["password"]
        )
        # Create famille / prestataire and link to user
        UserType = Prestataire if self.data["type"] == "prestataire" else Famille
        user = UserType(user=dj_user, email=self.cleaned_data["email"])
        user.save()

        # TODO: Send mail to verify user
        pass


class SimpleSearchForm(forms.Form):
    postal_code = forms.CharField(label="Code postal")


class FamilleForm(forms.ModelForm):
    class Meta:
        model = Famille
        exclude = ['created_at', 'updated_at', ]
