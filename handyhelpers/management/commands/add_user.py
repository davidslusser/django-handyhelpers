from django.core.management.base import BaseCommand

from handyhelpers.management.user_helpers import account_arguments, create_account, random_username


class Command(BaseCommand):
    help = "Create or update a user with explicit or independently generated credentials."
    generate_random_username = staticmethod(random_username)

    def add_arguments(self, parser):
        account_arguments(parser)
        parser.add_argument("--random", action="store_true")
        parser.add_argument("--prefix", default="")
        parser.add_argument("--suffix", default="")
        parser.add_argument("--length", type=int, default=8)

    def handle(self, *args, **options):
        create_account(self, options)
