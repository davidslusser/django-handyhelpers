Features
========

Conventional pages
------------------

``HandyHelperIndexView``, ``HandyHelperActionView``, ``HandyHelperAboutView``, and
``HandyHelperSingletonView`` support common page layouts. ``HandyHelperListView``
accepts a queryset/model and a model-specific ``table`` partial. It supports optional
``create_form_obj`` and ``filter_form_obj`` classes. Set ``*_form_modal_name``,
``*_form_url``, and other ``*_form_*`` attributes to configure the modals.
``HandyHelperPaginatedListView`` adds pagination and elided controls.

``FilterByQueryParamsMixin`` validates model fields, relations, lookups, and values.
Invalid filters return HTTP 400; they never fall back to unfiltered data. Extend
``filter_control_params`` for additional non-filter parameters or set ``filter_fields``
to restrict permitted roots. ``__in`` accepts comma-separated values, ``None`` means
SQL NULL, and true/false values are normalized. Lists must use deterministic ordering.

HTMX
----

The HTMX views provide full/partial rendering, card/list/table/minimal displays,
sidebar navigation, forms, modal creation, and action notifications. ``HX-Request``
must equal ``true``. Full/partial responses vary on this header.

``HtmxModelForm`` and ``HtmxForm`` render bound Django widgets with Bootstrap styling,
including initial values, choices, prefixes, hidden fields, and file uploads. Use
``as_bs5`` or ``as_bs5_disabled``. ``HtmxPostForm`` and ``CreateModelModalView`` return
HTML and HTTP 422 for invalid forms; the client swaps errors and keeps the modal open.
Successful creation returns HTTP 204 with the ``handyhelpers:created`` event. No form
errors or submitted passwords are retained in sessions.

``HtmxOptionMultiFilterView`` uses ``filter_form.cleaned_data`` for POST filtering.
Its invalid filters/forms return 400. Display links use named URL reversal, with a
query-parameter fallback for routes without a display argument.

Permissions
-----------

Django and DRF ``InAllGroups``/``InAnyGroup`` use ``permission_dict`` by HTTP method.
Omitted/None methods deny access, an explicit empty list permits access, and protected
methods require an authenticated group member or superuser. Anonymous Django requests
redirect to login; authenticated failures raise 403 (or safely redirect with a message
when ``MESSAGE_ON_PERMISSION_DENY`` is enabled).

``RequireLoginMiddleware`` must follow AuthenticationMiddleware. It checks before
executing views, uses path boundaries for exempt paths, and returns JSON 401 responses
for JSON requests. Group-based control visibility never substitutes for endpoint
permissions.

When django-auditlog is installed as an application, built-in audit routes require
login and the audited model's ``view`` permission. Entry lists distinguish app labels
and model names. The generic library does not implement object/tenant permissions;
projects requiring them must further restrict their audit views/querysets.

Reporting and exports
---------------------

Reports use 12 calendar months including the current partial month, timezone-aware
boundaries, and database aggregation. Summary day/week periods roll by 1/7 days;
month/year periods use calendar offsets. Trend charts show monthly additions;
progress charts include earlier records in cumulative totals. Color tokens are plain
Bootstrap names. Chart configurations are serialized with ``json_script``.

``count_by_hour``, ``count_by_week``, and ``count_by_month`` return newest-first lists
of 24, 52, and 12 counts respectively. Weekly buckets distinguish ISO year/week.
``CalendarView`` uses its configured ``event_model_date_field`` and named URL reversal;
``HtmxCalendarView`` can select a partial template.

``CsvExportView`` and ``ExcelExportView`` share strict query filtering. The latter
requires ``[excel]`` and writes .xlsx files. CSV strings with formula prefixes are
quoted as text; XLSX strings use the explicit string cell type. Datetimes are exported
as ISO strings. Configure endpoint authorization in your project.

API and models
--------------

The ``[api]`` extra supplies DRF and django-filter. ``InvalidLookupMixin`` validates
filters after authentication using ``filterset_class``/``filterset_fields``.
``PaginationControlMixin`` accepts true/1/yes to disable pagination.
``FkReadWriteField`` reads string representations and resolves writes against its
configured queryset. ``FlexFieldsMixin`` supports fields/omit query selection;
``ExcludeNullMixin`` removes null response values.

Model utilities include timestamp and singleton abstract models, managers, custom
``ne`` lookups, and non-empty character validation. Singleton save failures propagate;
instance deletion remains disabled. Existing project database fields are unchanged.
Presentation tags escape ordinary strings and distinguish zero from None.

Management commands
-------------------

``create_admin APP`` requires ``[admin]`` and accepts an app label, module, or AppConfig
path. It writes to the app directory by default. ``--output_file`` selects another
path; ``--force`` is required to overwrite an existing file::

    python manage.py create_admin myapp --output_file /tmp/admin.py

``add_user`` and ``add_superuser`` support custom user models. Use explicit credentials
or ``--generate-password``. ``--override`` updates the existing account without
replacing its primary key or relations. ``--field NAME VALUE`` supplies custom required
fields. ``add_user --random`` can generate an independent username/password;
``--prefix``, ``--suffix``, and ``--length`` configure usernames::

    python manage.py add_superuser --username admin --generate-password
    python manage.py add_user --random --length 16

Generated passwords appear once in command output. Store them securely.
The historical DRF generator commands are not included in this package.

Probes
------

``live/`` and ``ready/`` return process responses; they do not check external services.
``starttime/`` and ``uptime/`` expose process start time and elapsed time.
