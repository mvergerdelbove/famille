from django.conf import settings
from django.contrib.auth.decorators import login_required as django_login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from famille import forms
from famille.models import Famille, Prestataire, get_user_related, BaseFavorite
from famille.utils import get_context, get_result_template_from_user


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

def search(request):
    """
    Search view.
    """
    data = request.POST if request.method == "POST" else request.GET
    form = forms.SearchForm(data)
    if not form.is_valid():
        form = forms.SearchForm()

    # TODO: do location filtering, together with geolocation stuff
    objects = Prestataire.objects.all()[:settings.NB_SEARCH_RESULTS]
    template = get_result_template_from_user(request)
    if request.user.is_authenticated():
        favorites = get_user_related(request.user).favorites.all()
    else:
        favorites = []
    return render(
        request, "search.html",
        get_context(
            search_form=form, results=objects, result_template=template,
            nb_search_results=settings.NB_SEARCH_RESULTS,
            favorites=favorites, user=request.user
        )
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


# TODO: error handling for compte form
# TODO: redirect on right # on error
@login_required
def account(request):
    try:
        related = get_user_related(request.user)
    except ObjectDoesNotExist:
        raise Http404

    if request.method == "POST":
        account_forms = forms.AccountFormManager(instance=related, data=request.POST, files=request.FILES)
        if account_forms.is_valid():
            account_forms.save()
            return HttpResponseRedirect('/mon-compte/#' + account_forms.form_submitted)
    else:
        account_forms = forms.AccountFormManager(instance=related)

    return render(
        request, '%s_account.html' % account_forms.instance_type,
        get_context(**account_forms.forms)
    )


@require_POST
@login_required  # FIXME: does this work ?
def favorite(request):
    """
    Mark an object as favorite. If action=remove is passed,
    the given object is removed from favorites.
    """
    resource_uri = request.POST["resource_uri"]
    action_name = request.POST.get("action", "add")
    user_related = get_user_related(request.user)
    action = user_related.remove_favorite if action_name == "remove" else user_related.add_favorite
    action(resource_uri)

    return HttpResponse()
