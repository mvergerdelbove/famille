# -*- coding=utf-8 -*-
from itertools import chain, izip_longest

from django import forms
from django.contrib.auth.models import User
from localflavor.fr.forms import FRPhoneNumberField

from famille.models import Famille, Prestataire, Enfant, FamillePlanning
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


class ForeignKeyForm(object):

    foreign_model = None
    origin_model_name = None
    related_name = None
    sub_form = None

    def __init__(self, *args, **kwargs):
        self.objs_to_delete, objs, instance = [], [], None

        if kwargs.get("instance", None):
            instance = kwargs["instance"]
            objs = getattr(instance, self.related_name).all()

        if kwargs.get("data", None) is not None:
            data = pick(kwargs["data"], *self.sub_form.Meta.fields)
            data = self.unzip_data(data)
            objs, self.objs_to_delete = self.compute_objs_diff(data, objs, instance)
            data = izip_longest(data, objs)
            init_forms = lambda d: self.sub_form(data=d[0], instance=d[1])
            self.sub_forms = map(init_forms, data)
        else:
            self.sub_forms = map(
                lambda o: self.sub_form(instance=o), objs
            )

        # binding an empty form anyway
        self.sub_form_empty = self.sub_form()
        super(ForeignKeyForm, self).__init__(*args, **kwargs)

    def unzip_data(self, data):
        """
        Unzip a POST data to manage several
        related object instances.
        """
        try:
            nb_objs = len(data[self.sub_form.Meta.fields[0]])
        except KeyError:
            return []

        data_list = [{} for i in xrange(nb_objs)]
        for field, values in data.iteritems():
            for i, value in enumerate(values):
                data_list[i][field] = value

        return data_list

    def compute_objs_diff(self, data, objs, instance):
        """
        Find out the right number of related objects to be saved,
        given the data and the objects that are already present.

        :param data:       list of data for sub forms
        :param objs:       objs that are already there
        :param instance:   a model instance
        """
        objs_to_delete = []
        diff = len(data) - len(objs)
        # manage obj addition
        if diff > 0:
            kwargs = {self.origin_model_name: instance}
            objs = chain(
                objs,
                repeat_lambda(lambda: self.foreign_model(**kwargs), diff)
            )
        # manage obj deletion
        elif diff < 0:
            objs, objs_to_delete = isplit(objs, len(data))

        return objs, objs_to_delete

    def is_valid(self):
        """
        Validate the form and sub forms.
        """
        is_valid = super(ForeignKeyForm, self).is_valid()
        return all((f.is_valid() for f in self.sub_forms)) and is_valid

    def save(self, *args, **kwargs):
        """
        Save the form and sub forms.
        """
        for f in self.sub_forms:
            f.save(*args, **kwargs)

        [o.delete() for o in self.objs_to_delete]
        return super(ForeignKeyForm, self).save(*args, **kwargs)


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


class FamillePlanningSubForm(forms.ModelForm):
    class Meta:
        model = FamillePlanning
        labels = {
            "start_date": u"Choisir une date de début",
            "frequency": u"A quelle fréquence ?"
        }
        fields = labels.keys()
        widgets = {
            "start_date": forms.TextInput(attrs={'type':'datetime'}),
        }


class FamillePlanningForm(ForeignKeyForm, forms.ModelForm):
    foreign_model = FamillePlanning
    origin_model_name = "famille"
    related_name = "planning"
    sub_form = FamillePlanningSubForm

    class Meta:
        model = Famille
        fields = ()


class FamilleForm(ForeignKeyForm, UserForm):
    foreign_model = Enfant
    origin_model_name = "famille"
    related_name = "enfants"
    sub_form = EnfantForm

    class Meta(UserForm.Meta):
        model = Famille
        fields = UserForm.Meta.fields + ('type', )
        labels = dict(UserForm.Meta.labels, type="Type de famille")


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
            "profil": FamilleForm,
            "planning": FamillePlanningForm
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


class SimpleSearchForm(forms.Form):
    postal_code = forms.CharField(label="Code postal")


class SearchForm(forms.Form):
    # classic
    city = forms.CharField(
        label="Ville", required=False,
        widget=forms.TextInput(attrs={"data-api": "icontains"})
    )
    postal_code = forms.CharField(
        label="Code postal", required=False,
        widget=forms.TextInput(attrs={"data-api": "iexact"})
    ) # TODO : add completion on frontend
    type_garde = forms.MultipleChoiceField(
        label="Type de garde", choices=Prestataire.TYPES_GARDE.items(), required=False,
        widget=forms.SelectMultiple(attrs={"data-api": "in"})
    ) # TODO: add select2
    diploma = forms.MultipleChoiceField(
        label=u"Diplôme", choices=Prestataire.DIPLOMA.items(), required=False,
        widget=forms.SelectMultiple(attrs={"data-api": "in"})
    )
    language = forms.MultipleChoiceField(
        label=u"Langue(s) parlée(s)", choices=Prestataire.LANGUAGES.items(), required=False
    )
    tarif = forms.CharField(
        label=u"Tarif horaire (€/h)", widget=forms.TextInput(
            attrs={
                'type': 'text',
                'data-slider-min': '0',
                'data-slider-max': '80',
                'data-slider-step': '0.5'
            }
        ), required=False
    ) # TODO: range, not slider
    # extra 1
    cdt_periscolaire = forms.BooleanField(
        label=u"Conduite périscolaire", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )
    sortie_ecole = forms.BooleanField(
        label=u"Sortie d'école", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )
    baby = forms.BooleanField(
        label=u"Expérience avec bébés", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )
    devoirs = forms.BooleanField(
        label=u"Aide devoirs", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )
    menage = forms.BooleanField(
        label=u"Ménage", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )
    repassage = forms.BooleanField(
        label=u"Repassage", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )
    # extra 2
    psc1 = forms.BooleanField(
        label=u"Premiers secours", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )
    permis = forms.BooleanField(
        label=u"Permis voiture", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )
    urgence = forms.BooleanField(
        label=u"Garde d'urgence", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )
    nuit = forms.BooleanField(
        label=u"Garde de nuit", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )
    non_fumeur = forms.BooleanField(
        label=u"Non-fumeur", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )
