.. _internals:


Internals
=========

The documentation below details some of the internal workings of django-userextensions and its components. This
documentation is automatically generated from the source code. See the source code in github for full details.

https://github.com/davidslusser/django-handyhelpers


GUI Views
---------
.. automodule:: handyhelpers.views.gui
    :members: HandyHelperGenericBaseView, HandyHelperGenericBaseItemizedView, HandyHelperGenericBaseListView, HandyHelperActionView, HandyHelperAboutView, HandyHelperSingletonView, HandyHelperListView, HandyHelperListPlusCreateView, HandyHelperListPlusFilterView, HandyHelperListPlusCreateAndFilterView


Export Views
------------
.. automodule:: handyhelpers.views.export
    :members: CsvExportView, ExcelExportView


View Mixins
-----------
.. automodule:: handyhelpers.mixins.view_mixins
    :members: FilterByQueryParamsMixin


Viewset Mixins
--------------
.. automodule:: handyhelpers.mixins.viewset_mixins
    :members: InvalidLookupMixin, PaginationControlMixin


Permission Mixins
-----------------
.. automodule:: handyhelpers.permissions
    :members: InAllGroups, InAnyGroup


DRF Permission Mixins
---------------------
.. automodule:: handyhelpers.drf_permissions
    :members: IsInAllGroups, IsInAnyGroup

