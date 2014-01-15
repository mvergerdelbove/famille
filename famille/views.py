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

    if request.method == "POST":
        account_forms = forms.AccountFormManager(instance=related, data=request.POST)
        if account_forms.is_valid():
            account_forms.save()
            return HttpResponseRedirect('/mon-compte/#' + account_forms.form_submitted)
    else:
        account_forms = forms.AccountFormManager(instance=related)

    return render(
        request, '%s_account.html' % account_forms.instance_type,
        get_context(**account_forms.forms)
    )
