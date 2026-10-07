Release notes
=============

1.0.0
-----

* Target Django 5.2 LTS and Python 3.10–3.14; use modern Python packaging and extras.
* Remove vendored npm packages and Bootstrap 4 templates; use pinned CDN assets.
* Consolidate list/permission APIs and fix authentication timing and request isolation.
* Validate filters, preserve Django form widgets/uploads, and repair HTMX modal behavior.
* Protect audit logs with model permissions and distinguish app/model identifiers.
* Replace legacy XLS exports with XLSX; protect spreadsheet strings from formulas.
* Use portable aggregation, timezone-aware calendar periods, and safely serialized charts.
* Modernize account/admin-generation commands, documentation, and CI verification.

See :doc:`migration` for all breaking interfaces and replacements.

0.3.42
------

Previous release with mixed Bootstrap generations and vendored frontend packages.
