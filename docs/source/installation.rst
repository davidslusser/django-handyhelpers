Installation
============

Install the core Django utilities::

    pip install django-handyhelpers

Optional extras are ``api`` (DRF and django-filter), ``auditlog`` (django-auditlog),
``admin`` (Jinja2 admin generation), and ``excel`` (openpyxl). ``all`` enables every
runtime integration. ``dev`` and ``docs`` provide development tools::

    pip install 'django-handyhelpers[all]'

Add ``handyhelpers`` to ``INSTALLED_APPS`` and include its URL configuration::

    path('handyhelpers/', include('handyhelpers.urls'))

Add ``handyhelpers.context_processors.get_settings`` to your Django template context
processors. ``BASE_TEMPLATE`` defaults to ``handyhelpers/handyhelpers_base_bs5.htm``;
``handyhelpers/handyhelpers_with_sidebar.htm`` is available for sidebar layouts.
Views resolve explicit ``base_template`` overrides before the setting, at request time.

Assets
------

All external assets use pinned jsDelivr URLs with SHA-384 integrity hashes stored in
``handyhelpers/assets.json``. No npm installation is needed. Bootstrap includes Popper.
Chart.js, Bootstrap Table, and Clipboard.js load only for components that use them.
Optional JavaScript loads once across HTMX swaps. Custom assets remain in staticfiles.

Override the base template's ``core_assets``, ``icon_assets``, ``animation_assets``,
``project_theme``, or component includes to select another provider or self-host assets.
Custom base templates should load ``components.js``, ``charts.js``, and
``table_sortable.js`` after their core libraries. The optional ``asset_tags`` library
provides ``cdn_asset`` for the verified manifest entries. Sites that use a Content
Security Policy must allow their chosen script, style, and font origins and their
project's inline template scripts.
