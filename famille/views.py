from django.contrib.auth.decorators import login_required as django_login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from famille.forms import FamilleForm
from famille.models import Famille


login_required = django_login_required(
    redirect_field_name="s", login_url="auth_login"
)


@login_required
def account(request):
    if request.method == "POST":
        form = FamilleForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/mon-compte/')
    else:
        famille = Famille.objects.get(user=request.user)
        form = FamilleForm(instance=famille)

    # TODO : template
    return render(request, 'account.html', {
        'form': form,
    })
