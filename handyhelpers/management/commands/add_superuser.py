from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = 'Add a superuser'

    def __init__(self):
        self.opts = None
        super(Command, self).__init__()

    def add_arguments(self, parser):
        """ define command arguments """
        parser.add_argument('--username', type=str, help='name for new superuser')
        parser.add_argument('--password', type=str, help='password for new superuser')
        parser.add_argument('--email', type=str, default=None, help='email address for new superuser')
        parser.add_argument('--group', type=str, default=None, help='group this superuser account will be a member of')
        parser.add_argument('--override', action='store_true', required=False,
                            help='if superuser already exists, delete and create new superuser')

    def handle(self, *args, **options):
        """ command entry point """
        self.opts = options
        new_user = None

        # username is provided, but password was not
        if self.opts['username'] and not self.opts['password']:
            print('A password was not provided; password will be the same as the provided username.')
            self.opts['password'] = self.opts['username']

        # username was not provided, but password was
        if not self.opts['username'] and self.opts['password']:
            print('New superuser NOT created. Please provide a username, or leave both username and password blank to '
                  'use default values.')
            return

        # neither username nor password were provided
        if not self.opts['username'] and not self.opts['password']:
            self.opts['username'] = 'admin'
            self.opts['password'] = 'admin'

        # first check if user exists
        try:
            current_user = User.objects.get(username=self.opts['username'])
        except User.DoesNotExist:
            current_user = None

        if current_user:
            if self.opts['override']:
                User.objects.get(username=self.opts['username']).delete()
                print(f'''Deleted existing superuser `{self.opts['username']}` so new superuser could be created.''')
                new_user = User.objects.create_superuser(self.opts['username'],
                                                         self.opts['email'],
                                                         self.opts['password'])
                print(f'New superuser `{new_user}` created!')
            else:
                print(f'''A superuser with the username `{self.opts['username']}` already exists''')

        else:
            try:
                new_user = User.objects.create_superuser(self.opts['username'],
                                                         self.opts['email'],
                                                         self.opts['password'])
                print(f'New superuser `{new_user}` created!')
            except IntegrityError:
                print(f'''A superuser with the username `{self.opts['username']}` already exists''')

        # add and join group
        if self.opts['group']:
            group, is_group_new = Group.objects.get_or_create(name=self.opts['group'])
            if current_user:
                group.user_set.add(current_user)
            elif new_user:
                group.user_set.add(new_user)
