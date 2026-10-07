Migrating from 0.3 to 1.0
=========================

This is a breaking release. Upgrade projects to Python 3.10–3.14 and Django 5.2 LTS,
install the required extras, and migrate project overrides before deploying.

Python APIs
-----------

.. list-table:: Removed APIs and replacements
   :header-rows: 1
   :widths: 55 45

   * - Removed API
     - Replacement
   * - HandyHelperLegacyListView; HandyHelperBaseListView
     - HandyHelperListView
   * - HandyHelperBaseListPlusCreateView; HandyHelperListPlusCreateView
     - HandyHelperListView with create_form_obj
   * - HandyHelperListPlusFilterView
     - HandyHelperListView with filter_form_obj
   * - HandyHelperListPlusCreateAndFilterView
     - HandyHelperListView with both form attributes
   * - IsInAllGroups; IsInAnyGroup in drf_permissions
     - InAllGroups; InAnyGroup with permission_dict
   * - ExcludeNullMixin in viewset_mixins
     - ExcludeNullMixin in serializer_mixins
   * - AjaxGetView.template (preloaded template)
     - AjaxGetView.template_name (string path)

Rename ``create_form_modal``/``filter_form_modal`` to
``create_form_modal_name``/``filter_form_modal_name``. Group permission configuration
uses ``permission_dict`` consistently. Missing methods now deny access, including for
superusers. ``PaginationControlMixin`` now requires a true/1/yes value rather than
parameter presence. The all-groups template filter is ``in_all_groups`` (correcting
``in_all_group``). ``get_filtered_pagination_link`` now returns the complete encoded
query string: use ``?{{ page|get_filtered_pagination_link:query_string }}``, without
an additional ``page=`` prefix. ``byte_size`` now uses Django's filesizeformat.

Filtering
---------

Install ``[api]`` and replace rest_framework_filters with django_filters.rest_framework.
Use ``filterset_class`` or ``filterset_fields``. Replace RelatedFilter with explicit
related lookups, such as ``CharFilter(field_name='category__name')``. Legacy
``filter_class``, ``filter_fields`` on DRF views, and exclamation suffixes are removed.
GUI ``filter_fields`` remains an optional allowed-root list.

Invalid fields/lookups/values return 400. The old unfiltered/empty fallback settings
``HH_FILTERBYQUERYPARAM_NO_FILTER_ON_FAIL`` and ``HH_QUERY_PARAM_PREFIXES`` are removed.
Use explicit valid ORM paths and extend ``filter_control_params`` for additional
controls. ``INVALID_LOOKUP_SKIP_LIST`` still extends DRF control parameters.

Templates
---------

No Bootstrap 4 implementations or compatibility aliases remain. Migrate project
includes/extends and overrides using these mappings:

.. list-table:: Template replacements (all paths begin with handyhelpers/)
   :header-rows: 1
   :widths: 50 50

   * - Removed path
     - Replacement
   * - handyhelpers_base.htm
     - handyhelpers_base_bs5.htm
   * - generic/generic_about.html; generic/generic_action.html; generic/generic_index.html
     - Same filenames under generic/bs5/
   * - generic/generic_list.html; generic/generic_list_content.htm
     - Same filenames under generic/bs5/
   * - generic/generic_form.htm; generic/generic_form_wide.htm; generic/generic_error.html
     - Same filenames under generic/bs5/
   * - generic/generic_modal_form.htm; generic/generic_modal_form_wide.htm
     - Same filenames under generic/bs5/
   * - generic/generic_list_no_component.html; generic/generic_paginated_list_no_component.html
     - Same filenames under generic/bs5/
   * - generic/generic_paginated_list.html; generic/bs4/generic_paginated_list.html
     - generic/bs5/generic_list.html with HandyHelperPaginatedListView
   * - generic/generic_paginated_list_content.htm; generic/bs4/generic_paginated_list_content.htm
     - generic/bs5/generic_list_content.htm with is_paginated_view=True
   * - generic/bs4/generic_modal_form.htm; generic/bs4/generic_modal_form_wide.htm
     - Same filenames under generic/bs5/
   * - component/modals.htm; component/bs4/modals.htm
     - component/bs5/modals.htm
   * - component/show_messages.htm; component/bs4/show_messages.htm
     - component/bs5/show_messages.htm
   * - component/table_components.htm
     - component/bs5/table_components.htm
   * - component/bs5/mdb-form.htm
     - Bootstrap 5 form widgets/floating labels (no MDB helper)

The previous incorrect sidebar and table-wrapper defaults now resolve to
``htmx/bs5/navigation/sidebar_menu_sub_items.htm`` and ``htmx/bs5/table_wrapper.htm``.
The sidebar layout extends the canonical base. Keep project overrides compatible with
Bootstrap 5 attributes/classes and Font Awesome 7 icon names. Ordinary messages,
headings, and metadata are escaped; mark deliberately trusted HTML explicitly in
project code. Icons and rendered modal-body HTML remain trusted extension points.

Static delivery and HTMX
------------------------

Vendored node_modules and npm/yarn manifests are removed. Replace project-level local
vendor URLs with pinned CDN or self-hosted versions. The base template provides asset
blocks and the ``asset_tags`` library; see :doc:`installation`.

HTMX is upgraded to 2.0.11, jQuery to 4.0.0, and Chart.js to 4.5.1. Bootstrap uses its
5.3.8 bundle. Chart inputs are plain dictionaries/lists, not JavaScript expressions or
Python repr strings. Colors use Bootstrap tokens (for example ``primary``) or valid
CSS colors. ``get_color_list``/``get_colors`` no longer return executable ``theme.*``
expressions. Chart rendering initializes after assets load and HTMX swaps.

Invalid creation/inline forms return 422 HTML and remain open. Successful creation
returns 204 and emits ``handyhelpers:created`` with a message. Replace session-based
form-error handling and old creation toast-header assumptions with these responses.
Action views retain ``X-Toast-Message``, now rendered as text.

Exports, reports, and audit URLs
--------------------------------

``ExcelExportView`` requires ``[excel]`` and writes .xlsx instead of .xls. Update
filenames, content-type expectations, and client readers. ``xlwt`` is removed.
CSV formula-like strings are prefixed with an apostrophe; XLSX strings remain literal.

Annual reports now use 12 calendar months including the current partial month, and
calendar offsets for month/year summaries. Weekly/hourly/monthly aggregation counts
only the latest 52/24/12 buckets instead of combining matching buckets across years.
``get_annual_timestamps`` returns month starts, oldest first by default; ``reverse=True``
reverses that order. Chart drill-downs use complete encoded date boundaries.

Audit list URLs now include an app label::

    get_auditlog_entries/<app_label>/<model_name>/<pk>/

URL names are unchanged. Both list/detail routes require authentication and the
audited model's view permission. AJAX responses use application/json and retain
``server_response``. Templates are loaded lazily.

Commands and models
-------------------

Install ``[admin]`` for ``create_admin``. ``--force`` is required for overwrites.
Documented but absent ``generate_admin``/``generate_drf`` commands remain unavailable.
User commands require explicit or independently generated passwords. ``--override``
updates instead of deleting accounts. Use ``--field`` for custom required user fields.
Singleton integrity failures now propagate. No library database migration is required;
existing abstract model fields and primary-key defaults are preserved.
