from django.contrib.auth.decorators import login_required as django_login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from famille import forms
from famille.models import Famille
from famille.utils import get_context


login_required = django_login_required(
    redirect_field_name="s", login_url="auth_login"
)


def home(request):
    form = forms.SimpleSearchForm()
    return render(request, "home.html", get_context(form=form))

@login_required
def account(request):
    if request.method == "POST":
        form = forms.FamilleForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/mon-compte/')
    else:
        famille = Famille.objects.get(user=request.user)
        form = forms.FamilleForm(instance=famille)

    # TODO : template
    return render(request, 'account.html', get_context(form=form))
