# -*- coding=utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core import validators
from django.utils.functional import lazy
from localflavor.fr.forms import FRPhoneNumberField

from famille import data
from famille.models import (
    Famille, Prestataire, Enfant, FamillePlanning,
    Reference, PrestatairePlanning, UserInfo, FamilleRatings,
    PrestataireRatings, Criteria
)
from famille.models.planning import Schedule, Weekday, BasePlanning
from famille.models.utils import email_is_unique
from famille.utils.fields import (
    RangeField, LazyMultipleChoiceField, CommaSeparatedMultipleChoiceField,
    CommaSeparatedRangeField
)
from famille.utils.forms import ForeignKeyForm, ForeignKeyApiForm
from famille.utils.widgets import RatingWidget, RangeWidget


SCHEDULE_CHOICES = lazy(Schedule.get_choices, list)()
WEEKDAY_CHOICES = lazy(Weekday.get_choices, list)()


validate_email = validators.EmailValidator(message=u"Veuillez saisir un mail valide.")
validate_email_length = validators.MaxLengthValidator(100)  # make sure there is no 500 error...


class RegistrationForm(forms.Form):
    email = forms.CharField(label="Adresse mail", validators=[validate_email, validate_email_length])
    password = forms.CharField(
        label="Mot de passe", widget=forms.PasswordInput
    )

    def is_valid(self):
        if not super(RegistrationForm, self).is_valid():
            return False

        user_exists = bool(User.objects.filter(username=self.cleaned_data["email"]).first())
        if user_exists:
            self._errors["email"] = self.error_class([u"Un utilisateur existe déjà avec cet email."])

        return not user_exists

    def save(self, request):
        # Create user
        dj_user = User.objects.create_user(
            self.cleaned_data["email"],
            self.cleaned_data["email"],
            self.cleaned_data["password"]
        )
        dj_user.is_active = False
        dj_user.save()
        # Create famille / prestataire and link to user
        user = UserInfo.create_user(dj_user=dj_user, type=self.data["type"])
        user.send_verification_email(request)


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
            "tel_visible": u"J’accepte que mon téléphone soit visible pour les personnes souhaitant me contacter",
        }

    def is_valid(self):
        """
        Make sure the form is valid, additionally
        check that the email is unique among users.
        """
        if not super(UserForm, self).is_valid():
            return False

        if "email" not in self.changed_data:
            return True

        if not email_is_unique(self.cleaned_data["email"], self.instance):
            self._errors["email"] = self.error_class([u"Un utilisateur existe déjà avec cet email."])
            return False
        return True


    def save(self, commit=True):
        """
        Override save method to trigger geolocation if needed.
        """
        instance = super(UserForm, self).save(commit)
        if commit:
            instance.manage_geolocation(self.changed_data)
            if "email" in self.changed_data:
                instance.user.email = self.cleaned_data["email"]
                instance.user.save()
        return instance


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
        fields = UserForm.Meta.fields + ('type', 'description')
        labels = dict(UserForm.Meta.labels, type="Type de famille", description=u"Un peu plus de détails")
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "placeholder": u"Profitez de cet espace pour en dire plus sur votre famille"
                }
            )
        }


class CriteriaForm(forms.ModelForm):
    language = CommaSeparatedMultipleChoiceField(choices=data.LANGUAGES, required=False)
    diploma = CommaSeparatedMultipleChoiceField(choices=data.DIPLOMA, required=False)
    experience_type = CommaSeparatedMultipleChoiceField(choices=data.EXP_TYPES, required=False)
    tarif = CommaSeparatedRangeField(
        label=u"Tarif horaire (€/h)",
        widget=RangeWidget(
            min_value=settings.TARIF_RANGE[0],
            max_value=settings.TARIF_RANGE[1],
            attrs={"class": "form-control"}
        )
    )
    class Meta:
        labels = {
            "tarif": u"Tarif horaire (€/h)",
            "diploma": u"Diplômes/Formations garde d’enfants",
            "menage": u"Ménage",
            "repassage": "Repassage",
            "non_fumeur": "Non-fumeur",
            "devoirs": "Aide aux devoirs",
            "psc1": "Premiers secours",
            "permis": "Permis voiture",
            "description": u"Plus de détails",
            "language": u"Langues étrangères",
            "experience_type": u"Type d’expérience",
            "experience_year": u"Nombre d’années d’experiences",
            "studies": u"Niveau d'étude",
            "enfant_malade": u"Garde d'enfants handicapés",
            "cuisine": u"Cuisine",
            "animaux": u"Prend soin des animaux"
        }
        fields = labels.keys()
        widgets = {
            "description": forms.Textarea(
                attrs={
                    'rows': '5',
                }
            ),
        }


class FamilleCriteriaForm(CriteriaForm):
    type_garde = CommaSeparatedMultipleChoiceField(choices=data.TYPES_GARDE, required=False)
    class Meta(CriteriaForm.Meta):
        model = Famille
        labels = dict(
            CriteriaForm.Meta.labels, type_presta="Type de prestataire", type_garde="Type de garde"
        )
        fields = labels.keys()


class PrestataireForm(UserForm):
    type_garde = CommaSeparatedMultipleChoiceField(choices=data.TYPES_GARDE, required=False)

    class Meta(UserForm.Meta):
        model = Prestataire
        fields = UserForm.Meta.fields + ("type", "birthday", "other_type", "nationality", "type_garde")
        labels = dict(
            UserForm.Meta.labels,
            type=u"Vous êtes...",
            other_type="Autre",
            nationality=u"Nationalité",
            birthday=u"Date de naissance",
            type_garde=u"Type de garde"
        )
        widgets = {
            "birthday": forms.DateInput(
                attrs={'type':'datetime', "class": "form-control"},
                format="%d/%m/%Y"
            )
        }


class PrestataireCompetenceForm(CriteriaForm):
    class Meta(CriteriaForm.Meta):
        model = Prestataire
        labels = dict(
            CriteriaForm.Meta.labels, diploma=u"Diplôme",
            resume="Joindre un CV", description="Annonce"
        )
        fields = labels.keys()
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "placeholder": (u"Profitez de cet espace pour donner des "
                                    u"informations complémentaires sur vous !")
                }
            )
        }


class ReferenceForm(forms.ModelForm):
    class Meta:
        model = Reference
        labels = {
            "name": "Nom de famille",
            "email": "Adresse mail",
            "phone": u"Téléphone",
            "missions": "Missions",
            "referenced_user": "Nom de famille",
            "date_from": u"Période du...",
            "date_to": u"...au",
            "current": u"Je travaille toujours pour cette personne",
            "garde": u"Type de garde"
        }
        fields = labels.keys()
        widgets = {
            "date_from": forms.DateInput(
                attrs={'type':'datetime', "class": "form-control"},
                format="%d/%m/%Y"
            ),
            "date_to": forms.DateInput(
                attrs={'type':'datetime', "class": "form-control"},
                format="%d/%m/%Y"
            ),
        }


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
        "prestataire": u"Je recherche quelqu'un pour garder mes enfants",
        "famille": u"Je souhaite garder des enfants"
    }
    postal_code = forms.CharField(label="Code postal", required=False)
    type = forms.ChoiceField(label="Type de recherche", choices=SEARCH_TYPE.items())


class BaseSearchForm(forms.Form):
    # BOX 1
    pc = forms.CharField(
        label="Ville ou code postal", required=False,
        widget=forms.TextInput(attrs={"data-api": "iexact"})
    )
    distance = forms.CharField(
        required=False, widget=forms.HiddenInput(attrs={"data-api": "iexact"})
    )
    tarif = RangeField(
        label=u"Tarif horaire (€/h)",
        widget=RangeWidget(
            min_value=settings.TARIF_RANGE[0],
            max_value=settings.TARIF_RANGE[1],
            attrs={"class": "form-control"}
        )
    )
    # planning
    plannings__start_date = forms.CharField(
        label=u'À partir de', required=False,
        widget=forms.DateInput(
            attrs={'type':'datetime', "class": "form-control", "data-api": "gte"},
            format="%d/%m/%Y"
        )
    )
    plannings__weekday__id = LazyMultipleChoiceField(
        label=u"Jour(s) de la semaine", choices=WEEKDAY_CHOICES, required=False,
        widget=forms.SelectMultiple(attrs={"data-api": "in"})
    )
    plannings__frequency = forms.MultipleChoiceField(
        label=u"A quelle fréquence ?", choices=BasePlanning.FREQUENCY.items(), required=False,
        widget=forms.SelectMultiple(attrs={"data-api": "in"})
    )
    type = forms.MultipleChoiceField(
        label="Type de prestataire", choices=Prestataire.TYPES, required=False,
        widget=forms.SelectMultiple(attrs={"data-api": "in"})
    )
    type_garde = forms.MultipleChoiceField(
        label="Type de garde", choices=data.TYPES_GARDE, required=False,
        widget=forms.SelectMultiple(attrs={"data-api": "in"})
    )


class PrestataireSearchForm(BaseSearchForm):
    search_blocks = [
        {
            "key": "details",
            "label": u"Préciser mes besoins",
            "fields": ["nationality", "age", "language"],
        },
        {
            "key": "expertise",
            "label": u"Expertises recherchées",
            "fields": ["studies", "diploma", "experience_type", "experience_year"],
        },
        {
            "key": "plus",
            "label": u"Les petits + recherchés",
            "fields": [
                "enfant_malade", "menage", "repassage", "cuisine", "devoirs",
                "animaux", "permis", "voiture", "psc1", "non_fumeur"
            ]
        }
    ]

    ordering_dict = {
        "-updated_at": u"Le plus récent",
        "-rating": u"Le mieux noté"
    }
    # BOX 2
    nationality = forms.CharField(
        label=u"Nationalité", required=False,
        widget=forms.TextInput(attrs={"data-api": "iexact"})
    )
    age = forms.TypedChoiceField(
        label=u"Age", choices=Prestataire.AGES.items() + [('', '---------')], required=False,
        widget=forms.Select(attrs={"data-api": "exact"})  # FIXME: data-placeholder don't work
    )
    language = forms.MultipleChoiceField(
        label=u"Langue(s) parlée(s)", choices=data.LANGUAGES, required=False,
        widget=forms.SelectMultiple(attrs={"data-api": "in"})
    )
    # BOX 3
    studies = forms.MultipleChoiceField(
        label=u"Niveau d'études", choices=Criteria.STUDIES, required=False,
        widget=forms.SelectMultiple(attrs={"data-api": "in"})
    )
    diploma = forms.MultipleChoiceField(
        label=u"Diplômes liés à la garde d'enfant", choices=data.DIPLOMA, required=False,
        widget=forms.SelectMultiple(attrs={"data-api": "in"})
    )
    experience_type = forms.MultipleChoiceField(
        label=u"Type d'expérience", choices=data.EXP_TYPES, required=False,
        widget=forms.SelectMultiple(attrs={"data-api": "in"})
    )
    experience_year = forms.MultipleChoiceField(
        label=u"Années d'expérience", choices=Criteria.EXP_YEARS, required=False,
        widget=forms.SelectMultiple(attrs={"data-api": "in"})
    )
    # BOX 4
    enfant_malade = forms.BooleanField(
        label=u"Garde d'enfants malades", required=False,
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
    cuisine = forms.BooleanField(
        label=u"Cuisine", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )
    devoirs = forms.BooleanField(
        label=u"Aide devoirs", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )
    animaux = forms.BooleanField(
        label=u"Prends soin des animaux", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )
    psc1 = forms.BooleanField(
        label=u"Premiers secours", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )
    permis = forms.BooleanField(
        label=u"Permis voiture", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )
    voiture = forms.BooleanField(
        label=u"Possède une voiture", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )
    non_fumeur = forms.BooleanField(
        label=u"Non-fumeur", required=False,
        widget=forms.CheckboxInput(attrs={"data-api": "exact"})
    )


class FamilleSearchForm(BaseSearchForm):
    search_blocks = []
    ordering_dict = {
        "-updated_at": u"Le plus récent",
        "-rating": u"Le mieux noté"
    }
    type_attente_famille = forms.MultipleChoiceField(
        label=u"Type d'attentes", required=False, choices=Famille.TYPE_ATTENTES_FAMILLE,
        widget=forms.SelectMultiple(attrs={"data-api": "in"})
    )
    enfants__school = forms.CharField(
        label=u"Ecole des enfants", required=False,
        widget=forms.TextInput(attrs={"data-api": "icontains"})
    )
    n_enfants = forms.IntegerField(
        label=u"Nombre d'enfants", required=False,
        widget=forms.NumberInput(attrs={"data-api": "length"})
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
            "a": u"Fiabilité",
            "b": u"Relationnel",
            "c": u"Professionnalisme",
            "d": u"Flexibilité"
        }
        fields = labels.keys()
        widgets = {
            "a": RatingWidget(attrs={"star_class": "star-control", "class": "rating-score"}),
            "b": RatingWidget(attrs={"star_class": "star-control", "class": "rating-score"}),
            "c": RatingWidget(attrs={"star_class": "star-control", "class": "rating-score"}),
            "d": RatingWidget(attrs={"star_class": "star-control", "class": "rating-score"})
        }


class RatingFamilleForm(RatingBaseForm):

    class Meta(RatingBaseForm.Meta):
        model = FamilleRatings


class RatingPrestataireForm(RatingBaseForm):

    class Meta(RatingBaseForm.Meta):
        model = PrestataireRatings


class AdvancedForm(forms.ModelForm):

    class Meta:
        labels = {
            "visibility_family": (
                u"Je souhaite être visible auprès des familles "
            ),
            "visibility_prestataire": (
                u"Je souhaite être visible auprès des prestataires "
            ),
            "visibility_global": (
                u"Je souhaite être visible auprès de tout le monde"
            ),
            "newsletter": u"Je m'abonne à la newsletter",
        }
        fields = labels.keys()

    def __init__(self, *args, **kwargs):
        """
        Make sure the user has the right to edit visibility (premium).
        """
        super(AdvancedForm, self).__init__(*args, **kwargs)
        if self.instance and not self.instance.is_premium:
            self.fields['visibility_family'].widget.attrs['disabled'] = True
            self.fields['visibility_prestataire'].widget.attrs['disabled'] = True
            self.fields['visibility_global'].widget.attrs['disabled'] = True

            self.clean_visibility_family = lambda: self.instance.visibility_family
            self.clean_visibility_prestataire = lambda: self.instance.visibility_prestataire
            self.clean_visibility_global = lambda: self.instance.visibility_global


class FamilleAdvancedForm(AdvancedForm):

    class Meta(AdvancedForm.Meta):
        model = Famille


class PrestataireAdvancedForm(AdvancedForm):

    class Meta(AdvancedForm.Meta):
        model = Prestataire


class CustomAuthenticationForm(AuthenticationForm):
    error_messages = AuthenticationForm.error_messages
    error_messages["inactive"] = (
        u"Ce compte est inactif. Vous devez avoir reçu un "
        u"email d'activation. Dans le cas contraire, veuillez nous contacter"
    )
