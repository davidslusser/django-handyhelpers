from django.core.management.base import BaseCommand

from handyhelpers.management.user_helpers import account_arguments, create_account


class Command(BaseCommand):
    help = "Create or update a superuser with explicit or independently generated credentials."

    def add_arguments(self, parser):
        account_arguments(parser)
        parser.add_argument("--group")

    def handle(self, *args, **options):
        create_account(self, options, superuser=True)
