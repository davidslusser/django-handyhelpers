"""Account creation shared by the user management commands."""

import secrets
import string

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction


def create_account(command, options, superuser=False):
    model = get_user_model()
    username = options.get("username")
    if options.get("random") and not username:
        username = random_username(
            options.get("prefix", ""), options.get("suffix", ""), options.get("length", 8)
        )
    if not username:
        raise CommandError("Provide --username or --random.")
    password = options.get("password")
    generated = options.get("generate_password") or (options.get("random") and not password)
    if generated:
        password = secrets.token_urlsafe(24)
    if not password:
        raise CommandError("Provide --password or --generate-password.")
    fields = dict(options.get("field") or [])
    if model.USERNAME_FIELD in fields or any(
        name in fields for name in ("password", "is_staff", "is_superuser", "pk", "id")
    ):
        raise CommandError(
            "Use the dedicated account options instead of privilege/password/identity fields."
        )
    fields[model.USERNAME_FIELD] = username
    email_field = model.get_email_field_name()
    if options.get("email") is not None:
        fields[email_field] = options["email"]
    try:
        with transaction.atomic():
            current = (
                model._default_manager.select_for_update()
                .filter(**{model.USERNAME_FIELD: username})
                .first()
            )
            if current and not options.get("override"):
                raise CommandError(f"User {username} already exists; use --override to update it.")
            for name in model.REQUIRED_FIELDS:
                field = model._meta.get_field(name)
                if (
                    name not in fields
                    and current is None
                    and not field.blank
                    and not field.has_default()
                ):
                    raise CommandError(f"Provide required field {name} using --field {name} VALUE.")
            if current:
                for name, value in fields.items():
                    if name != model.USERNAME_FIELD:
                        setattr(current, name, value)
                current.set_password(password)
                if superuser:
                    current.is_staff = current.is_superuser = True
                current.full_clean(exclude=["password"])
                current.save()
                user = current
            else:
                method = (
                    model._default_manager.create_superuser
                    if superuser
                    else model._default_manager.create_user
                )
                user = method(password=password, **fields)
            if options.get("group"):
                user.groups.add(Group.objects.get_or_create(name=options["group"])[0])
    except (IntegrityError, TypeError, ValueError) as error:
        raise CommandError(str(error)) from error
    command.stdout.write(
        command.style.SUCCESS(f"User {username} {'updated' if current else 'created'}.")
    )
    if generated:
        command.stdout.write(f"Generated password: {password}")


def random_username(prefix="", suffix="", length=8):
    if length <= len(prefix) + len(suffix):
        raise CommandError("Length must exceed prefix and suffix lengths.")
    return (
        prefix
        + "".join(
            secrets.choice(string.ascii_letters + string.digits)
            for _ in range(length - len(prefix) - len(suffix))
        )
        + suffix
    )


def account_arguments(parser):
    parser.add_argument("--username")
    parser.add_argument("--password")
    parser.add_argument("--email")
    parser.add_argument("--generate-password", action="store_true")
    parser.add_argument(
        "--override",
        action="store_true",
        help="Update an existing user, preserving identity and relations.",
    )
    parser.add_argument("--field", nargs=2, action="append", metavar=("NAME", "VALUE"))
