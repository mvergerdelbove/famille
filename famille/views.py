from django.contrib.auth.decorators import login_required as django_login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views.decorators.http import require_POST

from famille import forms
from famille.models import Famille, Prestataire, get_user_related
from famille.utils import get_context


login_required = django_login_required(
    redirect_field_name="s", login_url="auth_login"
)


def home(request):
    """
    Home view. Rendering first forms.
    """
    search_form = forms.SimpleSearchForm()
    registration_form = forms.RegistrationForm()
    return render(
        request, "home.html",
        get_context(search_form=search_form, registration_form=registration_form)
    )


@require_POST
def register(request):
    """
    Register view. Allow user creation.
    """
    form = forms.RegistrationForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect('/confirmation/')

    # TODO: error
    pass


@login_required
def account(request):
    try:
        related = get_user_related(request.user)
    except ObjectDoesNotExist:
        raise Http404

    if isinstance(related, Famille):
        return famille_account(request, related)
    return prestataire_account(request, related)


def famille_account(request, famille):
    if request.method == "POST":
        hash = ""
        if request.POST["submit"] == "criteria":
            hash = "#attentes"
            criteria_form = forms.FamilleCriteriaForm(data=request.POST, instance=famille)
            form = forms.FamilleForm(instance=famille)
            form_to_validate = criteria_form
        else:
            criteria_form = forms.FamilleCriteriaForm(instance=famille)
            form = forms.FamilleForm(data=request.POST, instance=famille)
            form_to_validate = form

        if form_to_validate.is_valid():
            form_to_validate.save()
            return HttpResponseRedirect('/mon-compte/' + hash)
    else:
        form = forms.FamilleForm(instance=famille)
        criteria_form = forms.FamilleCriteriaForm(instance=famille)

    return render(
        request, 'famille_account.html',
        get_context(form=form, criteria_form=criteria_form)
    )


def prestataire_account(request, prestataire):
    if request.method == "POST":
#         hash = ""
#         if request.POST["submit"] == "criteria":
#             hash = "#attentes"
#             criteria_form = forms.FamilleCriteriaForm(data=request.POST, instance=famille)
#             form = forms.FamilleForm(instance=famille)
#             form_to_validate = criteria_form
#         else:
        # criteria_form = forms.FamilleCriteriaForm(instance=famille)
        form = forms.PrestataireForm(data=request.POST, instance=prestataire)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/mon-compte/')
    else:
        form = forms.PrestataireForm(instance=prestataire)
        # criteria_form = forms.FamilleCriteriaForm(instance=famille)

    return render(
        request, 'prestataire_account.html',
        get_context(form=form)
    )
