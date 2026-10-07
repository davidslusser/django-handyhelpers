"""Validate built archives and optionally smoke-test an installed distribution."""

import argparse
import importlib
import importlib.metadata
import sys
import tarfile
import zipfile
from pathlib import Path


def check_archive(path):
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
    else:
        with tarfile.open(path) as archive:
            names = archive.getnames()
    for name in names:
        assert not any(
            part in {"node_modules", "bs4", "tests", "handyhelpers_tests", "__pycache__"}
            for part in Path(name).parts
        ), name
        assert not name.endswith(("package.json", "package-lock.json", "yarn.lock", ".pyc")), name
    for required in [
        "handyhelpers/assets.json",
        "handyhelpers/templates/handyhelpers/handyhelpers_base_bs5.htm",
        "handyhelpers/static/handyhelpers/js/components.js",
        "handyhelpers/management/commands/admin_templates/admin.jinja",
    ]:
        assert any(name.endswith(required) for name in names), required
    print(f"{path.name}: archive contents verified")


def check_install(extra):
    from django.conf import settings

    apps = [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "handyhelpers",
    ]
    if extra in {"auditlog", "all"}:
        apps.append("auditlog")
    settings.configure(
        SECRET_KEY="smoke-test-only",
        INSTALLED_APPS=apps,
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        ROOT_URLCONF="handyhelpers.urls",
        TEMPLATES=[
            {"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True}
        ],
    )
    import django

    django.setup()
    importlib.import_module("handyhelpers.urls")
    importlib.import_module("handyhelpers.views")
    from django.template.loader import get_template

    from handyhelpers.templatetags.asset_tags import asset_manifest

    get_template("handyhelpers/handyhelpers_base_bs5.htm")
    assert len(asset_manifest()) == 13
    required = {
        "api": ["rest_framework", "django_filters"],
        "auditlog": ["auditlog"],
        "admin": ["jinja2"],
        "excel": ["openpyxl"],
    }
    modules = required.keys() if extra == "all" else [extra]
    for key in modules:
        for name in required.get(key, []):
            importlib.import_module(name)
    if extra == "core":
        assert "rest_framework" not in sys.modules and "openpyxl" not in sys.modules
        from django.core.exceptions import ImproperlyConfigured

        from handyhelpers.utils import optional_import

        for module, feature in [
            ("rest_framework", "api"),
            ("openpyxl", "excel"),
            ("auditlog", "auditlog"),
            ("jinja2", "admin"),
        ]:
            try:
                optional_import(module, feature)
            except ImproperlyConfigured:
                pass
            else:
                raise AssertionError(f"Core install unexpectedly includes {module}")
    print(
        f"Installed {importlib.metadata.version('django-handyhelpers')} [{extra}]: smoke checks passed"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", nargs="?", default="dist")
    parser.add_argument("--installed", choices=["core", "api", "auditlog", "admin", "excel", "all"])
    args = parser.parse_args()
    if args.installed:
        check_install(args.installed)
    else:
        archives = [*Path(args.directory).glob("*.whl"), *Path(args.directory).glob("*.tar.gz")]
        if not archives:
            raise SystemExit("No built distributions found")
        for archive in archives:
            check_archive(archive)
