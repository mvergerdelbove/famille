from collections import defaultdict

from django.conf import settings
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from famille import forms
from famille.models import (
    Famille, Prestataire, get_user_related, UserInfo,
    has_user_related, FamilleRatings, PrestataireRatings,
    compute_user_visibility_filters, DownloadableFile
)
from famille.resources import PrestataireResource, FamilleResource
from famille.utils import get_context, get_result_template_from_user, payment
from famille.utils.http import require_related, login_required, assert_POST


__all__ = [
    "home", "search", "register", "account",
    "favorite", "profile", "premium",
    "tools", "advanced", "delete_account",
    "premium_success", "premium_cancel"
]


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
        objects = Famille.objects.filter(compute_user_visibility_filters(request.user))
        template = "search/famille.html"
    else:
        FormClass = forms.PrestataireSearchForm
        objects = Prestataire.objects.all()
        template = "search/prestataire.html"

    form = FormClass(data)
    if not form.is_valid():
        form = FormClass()

    # TODO: do location filtering, together with geolocation stuff ?
    objects = objects.order_by("-updated_at")
    total_search_results = objects.count()
    nb_search_results = min(settings.NB_SEARCH_RESULTS, total_search_results)
    objects = objects[:nb_search_results]
    result_template = get_result_template_from_user(request)
    if request.user.is_authenticated():
        favorites = get_user_related(request.user).favorites.all()
    else:
        favorites = []
    return render(
        request, template,
        get_context(
            search_form=form, results=objects, result_template=result_template,
            nb_search_results=nb_search_results, ordering=form.ordering_dict,
            favorites=favorites, user=request.user, search_type=search_type,
            max_nb_search_results=settings.NB_SEARCH_RESULTS,
            total_search_results=total_search_results
        )
    )


def register(request, social=None, type=None):
    """
    Register view. Allow user creation.
    """
    if not type:
        if request.method == "POST":
            form = forms.RegistrationForm(request.POST)
            if form.is_valid():
                form.save()
        else:
            form = forms.RegistrationForm()
        return render(request, "registration/register.html", get_context(social=social, form=form))
    else:
        if not has_user_related(request.user):
            UserInfo.create_user(dj_user=request.user, type=type)
        else:
            return redirect('account')

    return HttpResponseRedirect('/confirmation/')


# TODO: error handling for compte form
@login_required
@require_related
def account(request):
    url_hash = ""
    if request.method == "POST":
        account_forms = forms.AccountFormManager(instance=request.related_user, data=request.POST, files=request.FILES)
        url_hash = account_forms.form_submitted
        if account_forms.is_valid():
            account_forms.save()
            return HttpResponseRedirect('/mon-compte/?success#%s' % url_hash)
    else:
        account_forms = forms.AccountFormManager(instance=request.related_user)

    return render(
        request, 'account/%s.html' % account_forms.instance_type,
        get_context(related=request.related_user, url_hash=url_hash, **account_forms.forms)
    )


@login_required
@require_related
@require_POST
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


@login_required
@require_related
@require_GET
def profile(request, type, uid):
    """
    Display the profile of a user.
    A nice 404 view is shown to the user
    if the profile does not exist OR the profile
    is not premium.
    A nice 401 view is shown to the user if the
    profile didn't want to show itself to the user
    or globally.
    """
    if type not in ("famille", "prestataire"):
        raise Http404

    context = {}

    if type == "famille":
        ModelClass = Famille
        RatingClass = FamilleRatings
        RatingFormClass = forms.RatingFamilleForm
    else:
        ModelClass = Prestataire
        RatingClass = PrestataireRatings
        RatingFormClass = forms.RatingPrestataireForm

    try:
        user = ModelClass.objects.get(pk=uid)
    except ModelClass.DoesNotExist:
        return render(request, "profile/404.html", status=404)

    # the user can view its own profile but others cannot if he is not premium
    if request.related_user != user and not user.is_premium:
        return render(request, "profile/404.html", status=404)

    if not user.profile_access_is_authorized(request):
        return render(request, "profile/401.html", status=401)

    if has_user_related(request.user):
        related_user = get_user_related(request.user)
        if not RatingClass.user_has_voted_for(related_user, user):
            rating = RatingClass(user=user, by=related_user.simple_id)
            context["rating_form"] = RatingFormClass(instance=rating)

    return render(request, "profile/base.html", get_context(profile=user, **context))


@login_required
@require_related
@require_GET
def premium(request):
    """
    Page to become premium.
    """
    if request.related_user.is_premium:
        return render(request, "account/already_premium.html", get_context())

    forms = payment.get_payment_forms(request.related_user, request)
    return render(request, "account/premium.html", get_context(payment_forms=forms))


@login_required
@require_related
@require_POST
@csrf_exempt
def premium_success(request):
    return render(request, "account/premium.html", get_context(action="success"))


@login_required
@require_related
@require_POST
@csrf_exempt
def premium_cancel(request):
    return HttpResponseRedirect("/devenir-premium/")


@login_required
@require_related
def advanced(request):
    """
    Render the advanved settings view. It is called by several views.
    """
    FormClass = forms.PrestataireAdvancedForm
    if isinstance(request.related_user, Famille):
        FormClass = forms.FamilleAdvancedForm

    if request.method == "POST":
        form = FormClass(instance=request.related_user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/mon-compte/parametres-avances/?success')
    else:
        form = FormClass(instance=request.related_user)

    return render(request, "account/advanced.html", get_context(form=form))


def tools(request):
    """
    Display the tools (DownloadableFile objects) to the user.
    """
    tool_files = defaultdict(list)
    for tool in DownloadableFile.objects.all():
        tool_files[tool.file_type].append(tool)

    return render(
        request, "espace/tools.html",
        get_context(tool_files=dict(tool_files), kinds=DownloadableFile.KINDS)
    )


@login_required
@require_related
@require_GET
def delete_account(request):
    """
    Mark an account as inactive.
    """
    request.user.is_active = False
    request.user.save()
    logout(request)
    return HttpResponseRedirect('/')
