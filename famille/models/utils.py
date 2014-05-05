from famille.models import Famille, Prestataire


def email_is_unique(email, model=None):
    """
    Verify that an email is unique among
    the database.

    :param email:        the email to verify
    :param model:        the input model. If
                         None, means that it's
                         a new user.
    """
    qs_famille = Famille.objects.filter(email=email)
    qs_presta = Prestataire.objects.filter(email=email)
    if model:
        if isinstance(model, Famille):
            qs_famille = qs_famille.exclude(pk=model.pk)
        else:
            qs_presta = qs_presta.exclude(pk=model.pk)

    return not qs_famille.count() and not qs_presta.count()
