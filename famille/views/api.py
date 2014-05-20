# -*- coding=utf-8 -*-
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST, require_GET

from famille import forms, models
from famille.utils.http import require_JSON, require_related, login_required, JsonResponse
from famille.utils.lookup import PostmanUserLookup
from famille.utils.mail import send_mail_from_template

__all__ = [
    "contact_favorites", "plannings", "profile_pic",
    "submit_rating", "message_autocomplete", "signal_user"
]


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

    request.related_user.send_mail_to_favorites(message, favorites)
    return HttpResponse()


@require_related
@require_POST
@require_JSON
@login_required
def plannings(request):
    """
    Manage planning updates for a given user.
    """
    if isinstance(request.related_user, models.Famille):
        FormClass = forms.FamillePlanningApiForm
    else:
        FormClass = forms.PrestatairePlanningApiForm

    form = FormClass(data=request.json, instance=request.related_user)
    if form.is_valid():
        form.save()
        return JsonResponse()

    return JsonResponse(form.sub_errors, status=400)


@require_related
@require_POST
@login_required
def profile_pic(request):
    """
    Manage planning updates for a given user.
    """
    if isinstance(request.related_user, models.Famille):
        FormClass = forms.ProfilePicFamilleForm
    else:
        FormClass = forms.ProfilePicPrestataireForm

    form = FormClass(instance=request.related_user, files=request.FILES)
    if form.is_valid():
        form.save()
        return JsonResponse({
            "profile_pic": form.instance.profile_pic.name
        })

    return JsonResponse(form.errors, status=403)


@require_related
@require_POST
@login_required
def submit_rating(request, type, uid):
    """
    A view to submit ratings for a user.
    """
    if type == "famille":
        ModelClass = models.Famille
        RatingClass = models.FamilleRatings
        RatingFormClass = forms.RatingFamilleForm
    else:
        ModelClass = models.Prestataire
        RatingClass = models.PrestataireRatings
        RatingFormClass = forms.RatingPrestataireForm

    user = get_object_or_404(ModelClass, pk=uid)
    if RatingClass.user_has_voted_for(request.related_user, user):
        return JsonResponse(status=401)

    rating = RatingClass(user=user, by=request.related_user.simple_id)
    form = RatingFormClass(instance=rating, data=request.POST)

    if form.is_valid():
        form.save()
        return JsonResponse({
            "total_rating": user.total_rating
        })

    return JsonResponse(form.errors, status=403)


lookup = PostmanUserLookup()


@require_related
@require_GET
@login_required
def message_autocomplete(request):
    """
    Retrieve users when writing messages (auto completion).
    """
    if not lookup.check_auth(request):
        return JsonResponse(status=403)

    query = request.GET.get("query")
    results = lookup.get_query_results(query)
    data = [lookup.format_result(result) for result in results]

    return JsonResponse({
        "objects": data
    })


@require_related
@require_POST
@login_required
def signal_user(request, userType, uid):
    """
    Signal a user by sending an email, using a reason.
    """
    reason = request.POST.get("reason")
    modelClass = models.Famille if userType == "famille" else models.Prestataire
    try:
        pk = int(uid)
    except (ValueError, TypeError):
        return HttpResponseBadRequest()

    user_to_signal = get_object_or_404(modelClass, pk=pk)
    send_mail_from_template(
        "email/signal_user.html", {
            "reason": reason, "user_to_signal": user_to_signal,
            "user": request.related_user
        }, subject=u"Un utilisateur a été signalé",
        recipient_list=[settings.CONTACT_EMAIL, ],
        from_email=settings.NOREPLY_EMAIL
    )

    return HttpResponse()
