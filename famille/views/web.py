import hashlib
import time

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.views.decorators.http import require_POST, require_GET
from paypal.standard.forms import PayPalPaymentsForm

from famille import forms
from famille.models import (
    Famille, Prestataire, get_user_related, UserInfo,
    has_user_related, FamilleRatings, PrestataireRatings,
    compute_user_visibility_filters
)
from famille.resources import PrestataireResource, FamilleResource
from famille.utils import get_context, get_result_template_from_user
from famille.utils.http import require_related, login_required, assert_POST


__all__ = [
    "home", "search", "register", "account",
    "favorite", "profile", "premium", "visibility",
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
@require_related
@login_required
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


@require_GET
def profile(request, type, uid):
    """
    Display the profile of a user.
    """
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
        return render(request, "profile/404.html")

    if not user.profile_access_is_authorized(request):
        return render(request, "profile/401.html")

    if has_user_related(request.user):
        related_user = get_user_related(request.user)
        if not RatingClass.user_has_voted_for(related_user, user):
            rating = RatingClass(user=user, by=related_user.simple_id)
            context["rating_form"] = RatingFormClass(instance=rating)

    return render(request, "profile/base.html", get_context(profile=user, **context))


premium_dict = {
    "business": settings.PAYPAL_RECEIVER_EMAIL,
    "amount": settings.PREMIUM_PRICE,
    "item_name": "Compte premium Une vie de famille",
    "item_number": settings.PREMIUM_ID,
    "src": "1",
    "currency_code": "EUR"
}

@require_related
@require_GET
@login_required
def premium(request, action=None):
    """
    Page to become premium.
    """
    if request.related_user.is_premium:
        return render_to_response("account/already_premium.html")

    if action == "valider":
        return render(request, "account/premium.html", get_context(action=action))

    data = premium_dict.copy()
    data.update(
        invoice="PREMIUM_VDF__%s__%s" % (int(time.time()), hashlib.md5(str(request.related_user.pk)).hexdigest()),
        notify_url=request.build_absolute_uri(reverse('paypal-ipn')),
        return_url=request.build_absolute_uri('/devenir-premium/valider/'),
        cancel_return=request.build_absolute_uri('/devenir-premium/annuler/')
    )
    form = PayPalPaymentsForm(button_type=PayPalPaymentsForm.SUBSCRIBE, initial=data)
    return render(request, "account/premium.html", get_context(form=form, action=action))


# FIXME: visibility for prestataires ?
@require_related
@login_required
def visibility(request):
    """
    Page to manage visibility on the website.
    """
    if request.method == "POST":
        form = forms.VisibilityForm(instance=request.related_user, data=request.POST)
        import pdb; pdb.set_trace()
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/mon-compte/visibilite/?success')
    else:
        form = forms.VisibilityForm(instance=request.related_user)

    return render(request, "account/visibility.html", get_context(form=form))
