# -*- coding=utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from localflavor.fr.forms import FRPhoneNumberField

from famille.models import (
    Famille, Prestataire, Enfant, FamillePlanning,
    Reference, PrestatairePlanning, UserInfo, FamilleRatings,
    PrestataireRatings
)
from famille.utils.fields import RangeField
from famille.utils.forms import ForeignKeyForm, ForeignKeyApiForm
from famille.utils.widgets import RatingWidget, RangeWidget


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
        UserInfo.create_user(dj_user=dj_user, type=self.data["type"])

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


class PlanningSubForm(forms.ModelForm):
    class Meta:
        labels = {
            "start_date": u"A partir de",
            "frequency": u"A quelle fréquence ?",
            "weekday": u"Jour(s) de la semaine",
            "schedule": u"Plage horaire",
        }
        fields = labels.keys()
        widgets = {
            "start_date": forms.DateInput(
                attrs={'type':'datetime', "class": "form-control"},
                format="%d/%m/%Y"
            )
        }


class FamillePlanningSubForm(PlanningSubForm):
    class Meta(PlanningSubForm.Meta):
        model = FamillePlanning


class PrestatairePlanningSubForm(PlanningSubForm):
    class Meta(PlanningSubForm.Meta):
        model = PrestatairePlanning


class BaseFamillePlanningForm(object):
    foreign_model = FamillePlanning
    origin_model_name = "famille"
    related_name = "planning"
    sub_form = FamillePlanningSubForm

    class Meta:
        model = Famille
        fields = ()

class BasePrestatairePlanningForm(object):
    foreign_model = PrestatairePlanning
    origin_model_name = "prestataire"
    related_name = "planning"
    sub_form = PrestatairePlanningSubForm

    class Meta:
        model = Prestataire
        fields = ()


class FamillePlanningForm(BaseFamillePlanningForm, ForeignKeyForm, forms.ModelForm):
    pass


class PrestatairePlanningForm(BasePrestatairePlanningForm, ForeignKeyForm, forms.ModelForm):
    pass


class FamillePlanningApiForm(BaseFamillePlanningForm, ForeignKeyApiForm, forms.ModelForm):
    key = "plannings"


class PrestatairePlanningApiForm(BasePrestatairePlanningForm, ForeignKeyApiForm, forms.ModelForm):
    key = "plannings"


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
        fields = UserForm.Meta.fields + ("type", "other_type")
        labels = dict(UserForm.Meta.labels, type="Type de prestataire", other_type=u"Précisez...")


class PrestataireCompetenceForm(CriteriaForm):
    class Meta(CriteriaForm.Meta):
        model = Prestataire
        fields = CriteriaForm.Meta.fields + [
            "level_en", "level_de", "level_es", "level_it", "other_language", "resume"
        ]
        labels = dict(
            CriteriaForm.Meta.labels, diploma=u"Diplôme", level_en="Anglais",
            level_de="Allemand", level_es="Espagnol", level_it="Italien",
            other_language="Autre langue", resume="Joindre un CV"
        )


class ReferenceForm(forms.ModelForm):
    class Meta:
        model = Reference
        labels = {
            "name": "Nom de famille",
            "email": "Adresse mail",
            "phone": u"Téléphone",
            "missions": "Missions",
            "referenced_user": "Nom de famille"
        }
        fields = labels.keys()


class PrestataireCompteForm(ForeignKeyForm, forms.ModelForm):
    foreign_model = Reference
    origin_model_name = "prestataire"
    related_name = "references"
    sub_form = ReferenceForm

    class Meta(UserForm.Meta):
        model = Prestataire
        fields = ()
        labels = {}


class AccountFormManager(object):
    base_form_classes = {
        "famille": {
            "attentes": FamilleCriteriaForm,
            "profil": FamilleForm,
            "planning": FamillePlanningForm
        },
        "prestataire": {
            "profil": PrestataireForm,
            "competences": PrestataireCompetenceForm,
            "compte": PrestataireCompteForm,
            "planning": FamillePlanningForm
        }
    }

    def __init__(self, instance, data=None, files=None):
        self.instance = instance
        self.instance_type = instance.__class__.__name__.lower()
        self.form_classes = self.base_form_classes[self.instance_type]
        self.data = data or {}
        self.files = files or {}
        self.form_submitted = self.data.get("submit", None)
        self.init_forms()

    def init_forms(self):
        """
        Initialize the forms using data and instance.
        """
        self.forms = {}
        for key, Form in self.form_classes.iteritems():
            if key == self.form_submitted:
                self.forms[key] = Form(data=self.data, files=self.files, instance=self.instance)
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
    SEARCH_TYPE = {
        "prestataire": "Un prestataire pour garder mes enfants",
        "famille": "Une famille pour garder mes enfants"
    }
    postal_code = forms.CharField(label="Code postal", required=False)
    type = forms.ChoiceField(label="Type de recherche", choices=SEARCH_TYPE.items())


class PrestataireSearchForm(forms.Form):
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
    tarif = RangeField(
        label=u"Tarif horaire (€/h)",
        widget=RangeWidget(min_value=5, max_value=100, attrs={"class": "form-control"})
    )
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


class FamilleSearchForm(forms.Form):
    type_garde = forms.MultipleChoiceField(
        label="Type de garde", choices=Famille.TYPES_GARDE_FAMILLE.items(), required=False,
        widget=forms.SelectMultiple(attrs={"data-api": "in"})
    ) # TODO: add select2
    cdt_periscolaire = forms.BooleanField(
        label=u"Conduite périscolaire", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )
    sortie_ecole = forms.BooleanField(
        label=u"Sortie d'école", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )

class ProfilePicBaseForm(forms.ModelForm):

    class Meta:
        fields = ("profile_pic", )


class ProfilePicFamilleForm(ProfilePicBaseForm):

    class Meta(ProfilePicBaseForm.Meta):
        model = Famille


class ProfilePicPrestataireForm(ProfilePicBaseForm):

    class Meta(ProfilePicBaseForm.Meta):
        model = Prestataire


class RatingBaseForm(forms.ModelForm):

    class Meta:
        labels = {
            "reliability": u"Fiabilité",
            "amability": u"Amabilité / Relationnel",
            "serious": u"Sérieux",
            "ponctuality": u"Ponctualité"
        }
        fields = labels.keys()
        widgets = {
            "reliability": RatingWidget(attrs={"star_class": "star-control", "class": "rating-score"}),
            "amability": RatingWidget(attrs={"star_class": "star-control", "class": "rating-score"}),
            "serious": RatingWidget(attrs={"star_class": "star-control", "class": "rating-score"}),
            "ponctuality": RatingWidget(attrs={"star_class": "star-control", "class": "rating-score"})
        }


class RatingFamilleForm(RatingBaseForm):

    class Meta(RatingBaseForm.Meta):
        model = FamilleRatings


class RatingPrestataireForm(RatingBaseForm):

    class Meta(RatingBaseForm.Meta):
        model = PrestataireRatings


class VisibilityForm(forms.ModelForm):

    class Meta:
        model = Famille
        labels = {
            "visibility_family": u"Visible auprès des familles",
            "visibility_prestataire": u"Visible auprès des prestataires",
            "visibility_global": u"Visible globalement sur le site",
        }
        fields = labels.keys()
