from django.views.decorators.http import require_POST

from famille import forms, models
from famille.utils.http import require_JSON, require_related, login_required, JsonResponse


__all__ = ["contact_favorites", "plannings"]


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
