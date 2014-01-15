# -*- coding=utf-8 -*-
from itertools import chain, izip_longest

from django import forms
from django.contrib.auth.models import User
from localflavor.fr.forms import FRPhoneNumberField

from famille.models import Famille, Prestataire, Enfant
from famille.utils import isplit, pick, repeat_lambda


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


class UserForm(forms.ModelForm):
    tel = FRPhoneNumberField(required=False)

    class Meta:
        fields = (
            'name', 'first_name', 'email', 'street',
            'postal_code', 'city', 'country',
            'tel', 'tel_visible'
        )
        labels = {
            "name": "Nom",
            "first_name": u"Prénom",
            "street": "Rue",
            "postal_code": "Code postal",
            "city": "Ville",
            "country": "Pays",
            "tel": u"Téléphone",
            "tel_visible": u"Téléphone visible",
        }


class FamilleForm(UserForm):
    class Meta(UserForm.Meta):
        model = Famille
        fields = UserForm.Meta.fields + ('type', )
        labels = dict(UserForm.Meta.labels, type="Type de famille")

    def __init__(self, *args, **kwargs):
        self.enfants_to_delete, enfants, instance = [], [], None

        if kwargs.get("instance", None):
            instance = kwargs["instance"]
            enfants = instance.enfants.all()

        if kwargs.get("data", None) is not None:
            data = pick(kwargs["data"], *EnfantForm.Meta.fields)
            data = EnfantForm.unzip_data(data)
            enfants, self.enfants_to_delete = self.compute_enfants_diff(data, enfants, instance)
            data = izip_longest(data, enfants)
            init_forms = lambda d: EnfantForm(data=d[0], instance=d[1])
            self.enfant_forms = map(init_forms, data)
        else:
            self.enfant_forms = map(
                lambda e: EnfantForm(instance=e), enfants
            )

        # binding an empty form anyway
        self.enfant_form_empty = EnfantForm()
        super(FamilleForm, self).__init__(*args, **kwargs)

    @staticmethod
    def compute_enfants_diff(data, enfants, instance):
        """
        Find out the right number of enfants to be saved,
        given the data and the enfants that are already present.

        :param data:       list of data for EnfantForm
        :param enfants:    enfants that are already there
        :param instance:   a Famille instance
        """
        enfants_to_delete = []
        diff = len(data) - len(enfants)
        # manage child addition
        if diff > 0:
            enfants = chain(
                enfants,
                repeat_lambda(lambda: Enfant(famille=instance), diff)
            )
        # manage child deletion
        elif diff < 0:
            enfants, enfants_to_delete = isplit(enfants, len(data))

        return enfants, enfants_to_delete

    def is_valid(self):
        """
        Validate the FamilleForm and the
        EnfantForms too.
        """
        is_valid = super(FamilleForm, self).is_valid()
        return all((e.is_valid() for e in self.enfant_forms)) and is_valid

    def save(self, *args, **kwargs):
        """
        Save the FamilleForm and the
        EnfantForms too.
        """
        for e in self.enfant_forms:
            e.save(*args, **kwargs)

        [e.delete() for e in self.enfants_to_delete]
        return super(FamilleForm, self).save(*args, **kwargs)


class EnfantForm(forms.ModelForm):
    class Meta:
        model = Enfant
        fields = ("e_name", "e_birthday", "e_school")
        labels = {
            "e_name": u"Prénom",
            "e_birthday": "Date de naissance",
            "e_school": u"Son école"
        }
        widgets = {
            "e_birthday": forms.TextInput(attrs={'type':'date'}),
        }

    @classmethod
    def unzip_data(cls, data):
        """
        Unzip a POST data to manage several
        Enfant instances.
        """
        try:
            nb_enfants = len(data[cls.Meta.fields[0]])
        except KeyError:
            return []

        data_list = [{} for i in xrange(nb_enfants)]
        for field, values in data.iteritems():
            for i, value in enumerate(values):
                data_list[i][field] = value

        return data_list


class CriteriaForm(forms.ModelForm):
    class Meta:
        labels = {
            "type_garde": "Type de garde",
            "tarif": u"Tarif horaire (€/h)",
            "diploma": u"Diplôme souhaité",
            "menage": u"Ménage",
            "repassage": "Repassage",
            "cdt_periscolaire": u"Conduite périscolaire",
            "sortie_ecole": u"Sortie d'école",
            "nuit": "Garde de nuit",
            "non_fumeur": "Non-fumeur",
            "devoirs": "Aide devoirs",
            "urgence": "Garde d'urgence",
            "psc1": "Premiers secours",
            "permis": "Permis voiture",
            "baby": u"Expérience avec bébés",
            "description": u"Plus de détails"
        }
        fields = labels.keys()
        widgets = {
            "tarif": forms.TextInput(
                attrs={
                    'type': 'text',
                    'data-slider-min': '0',
                    'data-slider-max': '80',
                    'data-slider-step': '0.5'
                }
            ),
            "description": forms.Textarea(
                attrs={
                    'rows': '5',
                }
            )
        }


class FamilleCriteriaForm(CriteriaForm):
    class Meta(CriteriaForm.Meta):
        model = Famille
        labels = dict(
            CriteriaForm.Meta.labels, type_presta="Type de prestataire",
            langue=u"Langue étrangère"
        )
        fields = labels.keys()


class PrestataireForm(UserForm):
    class Meta(UserForm.Meta):
        model = Prestataire
        fields = UserForm.Meta.fields + ("type", "sub_types")
        labels = dict(UserForm.Meta.labels, type="Type de prestataire")


class PrestataireCompetenceForm(CriteriaForm):
    class Meta(CriteriaForm.Meta):
        model = Prestataire
        fields = CriteriaForm.Meta.fields + [
            "level_en", "level_de", "level_es", "level_it", "other_language"
        ]
        labels = dict(
            CriteriaForm.Meta.labels, diploma=u"Diplôme", level_en="Anglais",
            level_de="Allemand", level_es="Espagnol", level_it="Italien",
            other_language="Autre langue"
        )


class AccountFormManager(object):
    base_form_classes = {
        "famille": {
            "attentes": FamilleCriteriaForm,
            "profil": FamilleForm
        },
        "prestataire": {
            "profil": PrestataireForm,
            "competences": PrestataireCompetenceForm
        }
    }

    def __init__(self, instance, data=None):
        self.instance = instance
        self.instance_type = instance.__class__.__name__.lower()
        self.form_classes = self.base_form_classes[self.instance_type]
        self.data = data or {}
        self.form_submitted = self.data.get("submit", None)
        self.init_forms()

    def init_forms(self):
        """
        Initialize the forms using data and instance.
        """
        self.forms = {}
        for key, Form in self.form_classes.iteritems():
            if key == self.form_submitted:
                self.forms[key] = Form(data=self.data, instance=self.instance)
            else:
                self.forms[key] = Form(instance=self.instance)

    def is_valid(self):
        """
        Validate the submitted form.
        """
        return self.form_submitted and self.forms[self.form_submitted].is_valid()

    def save(self):
        """
        Save the submitted form.
        """
        return self.forms[self.form_submitted].save()


class SearchForm(forms.Form):
    postal_code = forms.CharField(label="Code postal")
    type_garde = forms.MultipleChoiceField(label="Type de garde", choices=Prestataire.TYPES_GARDE.items())
    diploma = forms.MultipleChoiceField(label=u"Diplôme", choices=Prestataire.DIPLOMA.items())
    language = forms.MultipleChoiceField(label=u"Langue(s) parlée(s)", choices=Prestataire.LANGUAGES.items())

    class Meta:
        pass
