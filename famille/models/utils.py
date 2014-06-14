from django.db import transaction, IntegrityError

from famille.models import Famille, Prestataire, Criteria


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


def convert_user(user, NewClass):
    """
    Convert a user to a new class. Make sure we
    transfer as much data as possible.

    :param user:        the user instance
    :param NewClass:    the new user class
    """
    shared_fields = Criteria._meta.get_all_field_names() + ["language", ]
    type_field, new_type_field = ("type", "type_presta") if NewClass == Famille else ("type_presta", "type")
    django_user = user.user

    new_user = NewClass()
    setattr(new_user, new_type_field, getattr(user, type_field))
    for field_name in shared_fields:
        setattr(new_user, field_name, getattr(user, field_name))

    sid = transaction.savepoint()
    try:
        user.delete()
        new_user.user = django_user
        new_user.save()
        transaction.savepoint_commit(sid)
    except IntegrityError:
        transaction.savepoint_rollback()
        raise

    return new_user
