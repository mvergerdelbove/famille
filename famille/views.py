from django.conf import settings
from django.contrib.auth.decorators import login_required as django_login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from famille import forms
from famille.models import Famille, Prestataire, get_user_related, BaseFavorite
from famille.utils import get_context, get_result_template_from_user
from famille.utils.http import require_JSON, require_related


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
    search_type = data.get("type")
    search_type = "prestataire" if search_type not in ["famille", "prestataire"] else search_type
    if search_type == "famille":
        FormClass = forms.FamilleSearchForm
        Item = Famille
        template = "search_for_familles.html"
    else:
        FormClass = forms.PrestataireSearchForm
        Item = Prestataire
        template = "search_for_prestataires.html"

    form = FormClass(data)
    if not form.is_valid():
        form = FormClass()

    # TODO: do location filtering, together with geolocation stuff
    objects = Item.objects.all()[:settings.NB_SEARCH_RESULTS]
    result_template = get_result_template_from_user(request)
    if request.user.is_authenticated():
        favorites = get_user_related(request.user).favorites.all()
    else:
        favorites = []
    return render(
        request, template,
        get_context(
            search_form=form, results=objects, result_template=result_template,
            nb_search_results=settings.NB_SEARCH_RESULTS,
            favorites=favorites, user=request.user, search_type=search_type
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
@require_related
@login_required
def account(request):
    url_hash = ""
    if request.method == "POST":
        account_forms = forms.AccountFormManager(instance=request.related_user, data=request.POST, files=request.FILES)
        url_hash = account_forms.form_submitted
        if account_forms.is_valid():
            account_forms.save()
            return HttpResponseRedirect('/mon-compte/#' + url_hash)
    else:
        account_forms = forms.AccountFormManager(instance=request.related_user)

    return render(
        request, '%s_account.html' % account_forms.instance_type,
        get_context(related=request.related_user, url_hash=url_hash, **account_forms.forms)
    )


@require_related
@require_POST
@login_required  # FIXME: does this work ?
def favorite(request):
    """
    Mark an object as favorite. If action=remove is passed,
    the given object is removed from favorites.
    """
    resource_uri = request.POST["resource_uri"]
    action_name = request.POST.get("action", "add")
    user_related = request.related_user
    action = user_related.remove_favorite if action_name == "remove" else user_related.add_favorite
    action(resource_uri)

    return HttpResponse()


@require_related
@require_POST
@require_JSON
@login_required
def contact_favorites(request):
    """
    Contact favorites using mailer.
    """
    favorites = request.json["favorites"]
    message = request.json["message"]

    import pdb; pdb.set_trace()
    request.related_user.send_mail_to_favorites(message, favorites)
