from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
import string
import random


class Command(BaseCommand):
    help = 'Add a user'

    def __init__(self):
        self.opts = None
        super(Command, self).__init__()

    def add_arguments(self, parser):
        """ define command arguments """
        parser.add_argument('--username', type=str, help='name for new user')
        parser.add_argument('--password', type=str, help='password for new user')
        parser.add_argument('--email', type=str, default=None, help='email address for new user')
        parser.add_argument('--random', action='store_true', required=False, help='generate a random username')
        parser.add_argument('--prefix', type=str, default='', help='prefix to use when generating a random username')
        parser.add_argument('--suffix', type=str, default='', help='suffix to use when generating a random username')
        parser.add_argument('--length', type=int, default=8, help='length to use for random username')
        parser.add_argument('--override', action='store_true', required=False,
                            help='if superuser already exists, delete and create new superuser')

    @staticmethod
    def generate_random_username(prefix='', suffix='', length=8):
        """ generate a random username """
        prefix = str(prefix) if prefix else ''
        suffix = str(prefix) if suffix else ''
        chars = string.ascii_letters + string.digits
        return prefix + ''.join(random.choice(chars) for i in range(length - len(prefix))) + suffix

    def handle(self, *args, **options):
        """ command entry point """
        self.opts = options

        # exit without creating a new user entry if username is provided but password is not provided
        if self.opts['username'] and not self.opts['password']:
            print('New user NOT created. When specifying a username, please include also include a password.')
            return

        # exit without creating a new user entry if username and random are not provided but password is not provided
        if not self.opts['username'] and not self.opts['random'] and self.opts['password']:
            print('New user NOT created. Please provide a username OR add --random to generate a random username.')
            return

        # generate a random username with a provided password
        elif self.opts['random'] and self.opts['password'] and not self.opts['username']:
            self.opts['username'] = self.generate_random_username(prefix=self.opts['prefix'],
                                                                  suffix=self.opts['suffix'],
                                                                  length=self.opts['length'])

        # generate a random username and password (username == password)
        elif self.opts['random'] and not self.opts['password']:
            random_value = self.generate_random_username(prefix=self.opts['prefix'],
                                                         suffix=self.opts['suffix'],
                                                         length=self.opts['length'])
            self.opts['username'] = self.opts['password'] = random_value
            print('Generated a random username/password for you; (password == username).')

        # if not random, and not username and not password, use default values ('user')
        elif not self.opts['username'] and not self.opts['password']:
            self.opts['username'] = 'user'
            self.opts['password'] = 'user'

        # first check if user exists
        try:
            current_user = User.objects.get(username=self.opts['username'])
        except User.DoesNotExist:
            current_user = None

        if current_user:
            if self.opts['override']:
                User.objects.get(username=self.opts['username']).delete()
                print(f'''Deleted existing user {self.opts['username']} so new user could be created.''')
                new_user = User.objects.create_user(self.opts['username'], self.opts['email'], self.opts['password'])
                print(f'New user {new_user} created!')
            else:
                print(f'''A user with the username `{self.opts['username']}` already exists.''')

        else:
            try:
                new_user = User.objects.create_user(self.opts['username'], self.opts['email'], self.opts['password'])
                print(f'New user `{new_user}` created!')
            except IntegrityError:
                print(f'''A user with the username `{self.opts['username']}` already exists.''')
