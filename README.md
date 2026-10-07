# django-handyhelpers

Reusable Django views, Bootstrap 5 templates, HTMX components, and model/API utilities.

Version 1.0 is a breaking modernization release for **Python 3.10–3.14 and Django 5.2 LTS**.
Read the [migration guide](docs/source/migration.rst) before upgrading from 0.3.

## Installation

```bash
pip install django-handyhelpers
# Optional integrations:
pip install 'django-handyhelpers[api,auditlog,admin,excel]'
# Or every runtime integration:
pip install 'django-handyhelpers[all]'
```

Add `handyhelpers` to `INSTALLED_APPS`. Include its URL configuration:

```python
INSTALLED_APPS = [
    # Django apps ...
    "handyhelpers",
]
urlpatterns = [path("handyhelpers/", include("handyhelpers.urls"))]
```

Add `handyhelpers.context_processors.get_settings` to the template context processors
for project metadata and `BASE_TEMPLATE`. Built-in views resolve `BASE_TEMPLATE` at
request time; the default is `handyhelpers/handyhelpers_base_bs5.htm`. A sidebar layout
is available as `handyhelpers/handyhelpers_with_sidebar.htm`.

## Features

- Generic index, action, about, singleton, list, and paginated pages.
- Optional create/filter forms on conventional lists; strict ORM query filtering.
- HTMX partials, detail views, multiple display modes, forms/uploads, modal creation,
  sidebar navigation, actions, and toasts.
- Timezone-aware calendars, statistics, annual trend/cumulative charts, and portable
  hourly/weekly/monthly aggregation.
- CSV and optional `.xlsx` exports, safe against spreadsheet formula interpretation.
- Abstract timestamp/singleton models, managers, model/form mixins, and template tags.
- Method/group permissions, login middleware, optional DRF filtering/serializers, and
  permission-protected audit-log endpoints.
- `create_admin`, `add_user`, and `add_superuser` management commands.

```python
from handyhelpers.views import HandyHelperPaginatedListView


class ItemList(HandyHelperPaginatedListView):
    queryset = Item.objects.order_by("pk")
    title = "Items"
    table = "items/table.htm"
    paginate_by = 25
```

`table` is your model-specific table partial. Authorize views/action endpoints in your
project; hiding a create button by group is presentation, not authorization.

Frontend dependencies use **pinned jsDelivr URLs with integrity hashes**. No npm install
or frontend build is required. Project-owned CSS/JS still use Django staticfiles.
Override `core_assets`, `icon_assets`, `animation_assets`, `project_theme`, or component
includes to use another asset provider or self-hosted files.

## Development

```bash
python -m pip install -e '.[dev,docs]'
pytest -m 'not browser'
ruff check .
ruff format --check .
python -m sphinx -W --keep-going -b html docs/source /tmp/handyhelpers-docs
python -m build
python -m twine check dist/*
```

Browser tests use the shipped templates and actual pinned CDN assets:

```bash
python -m playwright install chromium
pytest -m browser
```

For PostgreSQL portability tests, set `HH_TEST_POSTGRES=1` and the usual `PGDATABASE`,
`PGUSER`, `PGPASSWORD`, `PGHOST`, and `PGPORT` variables. CI checks Python 3.10–3.14,
SQLite/PostgreSQL, browser interactions, docs, optional installs, and distribution contents.

Full documentation: https://django-handyhelpers.readthedocs.io/
