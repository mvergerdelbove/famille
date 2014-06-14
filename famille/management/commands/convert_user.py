from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from famille.models import Famille, Prestataire
from famille.models.utils import convert_user


class Command(BaseCommand):
    args = "<email> <type>"
    help = "Convert a given user into another type (prestataire or famille)."

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError("This command takes exactly two arguments: %s" % self.args)

        email, user_type = args
        user_type = user_type.lower()
        if user_type not in ("famille", "prestataire"):
            raise CommandError("Unknown user type %s" % user_type)

        # find the user in the opposite type
        UserClass, NewClass = (Famille, Prestataire) if user_type == "prestataire" else (Prestataire, Famille)
        try:
            user = UserClass.objects.get(email=email)
        except UserClass.DoesNotExist:
            raise CommandError("User with email %s does not exists")

        convert_user(user, NewClass)
