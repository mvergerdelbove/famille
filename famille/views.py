from django.contrib.auth.decorators import login_required as django_login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_POST

from famille import forms
from famille.models import Famille
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
    famille = Famille.objects.get(user=request.user)
    if request.method == "POST":
        import pdb; pdb.set_trace()
        form = forms.FamilleForm(data=request.POST, instance=famille)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/mon-compte/')
    else:
        form = forms.FamilleForm(instance=famille)

    # TODO : template
    return render(request, 'account.html', get_context(form=form))
