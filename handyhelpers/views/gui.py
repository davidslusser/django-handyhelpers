from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic import ListView, View

from handyhelpers.mixins.view_mixins import FilterByQueryParamsMixin


class HandyHelperGenericBaseView(View):
    """ Generic view used to set the base_template variable. This extends django.view.generic.View and will use the base
     template defined in the BASE_TEMPLATE settings variable or use handyhelpers/handyhelpers_base_bs5.htm if not provided.

    class parameters:
        base_template - base template used for rendering page; defaults to: handyhelpers_base.htm
        args          - additional args to pass into the template
        kwargs        - additional kwargs to pass into the template
    """
    base_template = getattr(settings, 'BASE_TEMPLATE', 'handyhelpers/handyhelpers_base_bs5.htm')
    args = None
    kwargs = None


class HandyHelperGenericBaseItemizedView(HandyHelperGenericBaseView):
    """ Generic view to include shared variables used in views itemized views, such as index and action views.

    class parameters:
        base_template        - base template used for rendering page; defaults to: handyhelpers_base.htm
        args                 - additional args to pass into the template
        kwargs               - additional kwargs to pass into the template
        title                - page title to use; will display in a H1 element
        subtitle             - subtitle to use; will display in a H5 element (None if not provided)
        item_list            - list of items/actions to display (one per card)
        protected_item_list  - list of items/action only visible to members of protected_group_name
        protected_group_name - name of group to show protected_item_list items to
    """
    title = None
    subtitle = None
    item_list = None
    protected_item_list = None
    protected_group_name = None


class HandyHelperGenericBaseListView(FilterByQueryParamsMixin, ListView):
    """ Generic list view used to set the base_template, template, title, table, and modal variables. This extends
    django.view.generic.ListView and will use the base template defined in the BASE_TEMPLATE settings variable or use
    handyhelpers/handyhelpers_base_bs5.htm if not provided. This view also includes the
    handyhelpers.mixins.view_mixins.FilterByQueryParamsMixin mixin to allow filtering by query parameters.

    class parameters:
        base_template - base template used for rendering page; defaults to: handyhelpers_base.htm
        template_name - template used when rendering page; defaults to: handyhelpers/generic/generic_list.html
        title         - title to use in template
        table         - htm file rendering the queryset to be included in the generic_list template
        modals        - htm file rendering additional modals to be included in the generic_list template
        add_static    - additional static file to include on the template
        add_template  - additional template to include on the template
    """
    base_template = getattr(settings, 'BASE_TEMPLATE', 'handyhelpers/handyhelpers_base_bs5.htm')
    template_name = 'handyhelpers/generic/bs5/generic_list.html'
    title = None
    table = None
    modals = None
    add_static = None
    add_template = None
    args = None
    kwargs = None


class HandyHelperIndexView(HandyHelperGenericBaseItemizedView):
    """
    View to render an index page with actions/options listed as 'zoom-cards' in flex-box container(s)

    class parameters:
        base_template        - base template used for rendering page; defaults to: handyhelpers_base.htm
        template_name        - template used when rendering page; defaults to: handyhelpers/generic/generic_index.html
        title                - page title to use; will display in a H1 element
        subtitle             - subtitle to use; will display in a H5 element (None if not provided)
        item_list            - list of items/actions to display (one per card)
        protected_item_list  - list of items/action only visible to members of protected_group_name
        protected_group_name - name of group to show protected_item_list items to
    """
    template_name = 'handyhelpers/generic/bs5/generic_index.html'

    def get(self, request):
        context = dict(base_template=self.base_template, title=self.title, subtitle=self.subtitle,
                       item_list=self.item_list, protected_item_list=self.protected_item_list,
                       protected_group_name=self.protected_group_name, args=self.args, kwargs=self.kwargs)
        return render(request, self.template_name, context)


class HandyHelperActionView(HandyHelperGenericBaseItemizedView):
    """
    Action page with actions/options listed as 'zoom-cards' in flex-box container(s)

    class parameters:
        base_template        - base template used for rendering page; defaults to: handyhelpers_base.htm
        args                 - additional args to pass into the template
        kwargs               - additional kwargs to pass into the template
        template_name        - template used when rendering page; defaults to: handyhelpers/generic/bs5/generic_action.html
        title                - page title to use; will display in a H1 element
        subtitle             - subtitle to use; will display in a H5 element (None if not provided)
        item_list            - list of items/actions to display (one per card)
        protected_item_list  - list of items/action only visible to members of protected_group_name
        protected_group_name - name of group to show protected_item_list items to
        form_list            - list of django forms used in page
    """
    template_name = 'handyhelpers/generic/bs5/generic_action.html'
    form_list = None

    def get(self, request):
        context = dict(base_template=self.base_template, title=self.title, subtitle=self.subtitle,
                       item_list=self.item_list, form_list=self.form_list, protected_item_list=self.protected_item_list,
                       protected_group_name=self.protected_group_name, args=self.args, kwargs=self.kwargs)
        return render(request, self.template_name, context)


class HandyHelperAboutView(HandyHelperGenericBaseView):
    """
    Generic view to render an 'about' page.

    class parameters:
        base_template - base template used for rendering page; defaults to: handyhelpers_base.htm
        args          - additional args to pass into the template
        kwargs        - additional kwargs to pass into the template
        template_name - template used when rendering page; defaults to: handyhelpers/generic/generic_about.html
        title         - page title to use ('About' if not provided)
        subtitle      - subtitle to use (None if not provided)
        version       - version to display (None if not provided)
        details       - any specific details to display (None if not provided)
        source        - link to source code repository (None if not provided)
        contact       - any desired contact information (None if not provided)
        links         - list of dictionary containing links; ex. [{'some reference': 'www.somewebsite.com}, ...]
    """
    template_name = 'handyhelpers/generic/bs5/generic_about.html'
    title = 'About'
    subtitle = None
    version = None
    details = None
    source = None
    contact = None
    links = []

    def get(self, request):
        context = dict(base_template=self.base_template, title=self.title, subtitle=self.subtitle, version=self.version,
                       details=self.details, source=self.source, contact=self.contact, links=self.links,
                       args=self.args, kwargs=self.kwargs)
        return render(request, self.template_name, context)


class HandyHelperSingletonView(HandyHelperGenericBaseView):
    """
    View for rendering a page based on a SingletonModel

    class parameters:
        base_template - base template used for rendering page; defaults to: handyhelpers_base.htm
        args          - additional args to pass into the template
        kwargs        - additional kwargs to pass into the template
        template_name - template used when rendering page
        model         - singleton model
    """
    template_name = None
    model = None

    def get(self, request):
        context = dict(object=self.model.objects.get(), args=self.args, kwargs=self.kwargs)
        return render(request, self.template_name, context)


class HandyHelperListView(HandyHelperGenericBaseListView):
    """
    A reusable generic base view to render a ListView where the child view will provide a html table.

    class parameters:
        base_template    - base template used for rendering page; defaults to: handyhelpers_base.htm
        template_name    - template used when rendering page; defaults to: handyhelpers/generic/generic_list.html
        args             - additional args to pass into the template
        kwargs           - additional kwargs to pass into the template
        queryset         - queryset to be rendered on the page
        title            - title to use in template
        page_description - subtitle to use in template
        table            - htm file rendering the queryset to be included in the generic_list template
        modals           - htm file rendering additional modals to be included in the generic_list template
        add_static       - additional static file to include on the template
        add_template     - additional template to include on the template

    example:
        class ListProjects(HandyHelperBaseListView):
            queryset = Project.objects.all()
            title = 'Projects'
            page_description = 'my cool projects'
            table = 'table/table_projects.htm'
            modals = 'project_modals.htm'
    """
    def get(self, request, *args, **kwargs):
        context = dict(base_template=self.base_template, queryset=self.filter_by_query_params(), title=self.title,
                       subtitle=self.page_description, table=self.table, modals=self.modals,
                       add_static=self.add_static, add_template=self.add_template,
                       args=self.args, kwargs=self.kwargs)
        return render(request, self.template_name, context)


class HandyHelperBaseListView(HandyHelperListView):
    """ maintaining the HandyHelperBaseListView for legacy compatibility """
    pass


class HandyHelperListPlusCreateView(HandyHelperGenericBaseListView):
    """
    A reusable generic base view to render a ListView where the child view will provide a html table and create form.

    class parameters:
        base_template                - base template used for rendering page; defaults to: handyhelpers_base.htm
        template_name                - template used when rendering page;
                                       defaults to: handyhelpers/generic/generic_list.html
        args                         - additional args to pass into the template
        kwargs                       - additional kwargs to pass into the template
        queryset                     - queryset to be rendered on the page
        title                        - title to use in template
        page_description             - subtitle to use in template
        table                        - htm file rendering the queryset to be included in the generic_list template
        modals                       - htm file rendering additional modals to be included in the generic_list template
        add_static                   - additional static file to include on the template
        add_template                 - additional template to include on the template
        allow_create_groups          - comma separated list of groups that are allowed to create a new record

        create_form_obj              - form object
        create_form_url              - url the form (action) should post to
        create_form_title            - title to use on the create form modal (can be html)
        create_form_modal            - name of modal for the create form
        create_form_modal_backdrop   - optional data-backdrop value(such as data-backdrop="static")
        filter_form_modal_scrollable - add vertical scrolling to modal body
        create_form_modal_size       - bootstrap modal size class (such as modal-lg)
        create_form_link_title       - text used for the link opening the create form
        create_form_tool_tip         - text to use for the tooltip
        create_form_autocomplete     - autocomplete parameter to use in form tag (on/off)

    example:
        class ListProjects(HandyHelperBaseCreateListView):
            queryset = Project.objects.all()
            title = 'Projects'
            page_description = 'my cool projects'
            table = 'table/table_projects.htm'

            create_form_obj = ProjectForm
            create_form_url = '/hostmgr/create_project/'
            create_form_title = '<b>Add Project: </b><small> </small>'
            create_form_modal = 'add_project'
            create_form_modal_size = 'modal-lg'
            create_form_modal_backdrop = 'static'
            create_form_link_title = 'add project'
            create_form_tool_tip = 'add project'
    """
    create_form = dict()
    create_form_obj = None
    create_form_id = None
    create_form_url = None
    create_form_title = None
    create_form_modal = None
    create_form_modal_size = None
    create_form_modal_backdrop = None
    create_form_link_title = None
    create_form_tool_tip = None
    create_form_autocomplete = None
    allow_create_groups = None

    def get(self, request, *args, **kwargs):
        context = dict(base_template=self.base_template, queryset=self.filter_by_query_params(), title=self.title,
                       subtitle=self.page_description, table=self.table, modals=self.modals,
                       add_static=self.add_static, add_template=self.add_template,
                       allow_create_groups=self.allow_create_groups, args=self.args, kwargs=self.kwargs)
        if self.create_form_obj:
            self.create_form['form'] = self.create_form_obj(request.POST or None)
            self.create_form['form_id'] = self.create_form_id
            self.create_form['action'] = 'Add'
            self.create_form['action_url'] = self.create_form_url
            self.create_form['title'] = self.create_form_title
            self.create_form['modal_name'] = self.create_form_modal
            self.create_form['modal_size'] = self.create_form_modal_size
            self.create_form['modal_backdrop'] = self.create_form_modal_backdrop
            self.create_form['link_title'] = self.create_form_link_title
            self.create_form['tool_tip'] = self.create_form_tool_tip
            self.create_form['autocomplete'] = self.create_form_autocomplete
            context['create_form'] = self.create_form
        return render(request, self.template_name, context)


class HandyHelperBaseListPlusCreateView(HandyHelperListView):
    """ maintaining the HandyHelperBaseListPlusCreateView for legacy compatibility """
    pass


class HandyHelperListPlusFilterView(HandyHelperGenericBaseListView):
    """
    A reusable generic base view to render a ListView where the child view will provide a html table and filter form.

    class parameters:
        base_template                - base template used for rendering page; defaults to: handyhelpers_base.htm
        template_name                - template used when rendering page;
                                       defaults to: handyhelpers/generic/generic_list.html
        args                         - additional args to pass into the template
        kwargs                       - additional kwargs to pass into the template
        queryset                     - queryset to be rendered on the page
        title                        - title to use in template
        page_description             - subtitle to use in template
        table                        - htm file rendering the queryset to be included in the generic_list template
        modals                       - htm file rendering additional modals to be included in the generic_list template
        add_static                   - additional static file to include on the template
        add_template                 - additional template to include on the template

        filter_form_obj              - form object
        filter_form_url              - url the form (action) should post to
        filter_form_title            - title to use on the filter form modal (can be html)
        filter_form_modal            - name of modal for the filter form
        filter_form_modal_backdrop   - optional data-backdrop value(such as data-backdrop="static")
        filter_form_modal_scrollable - add vertical scrolling to modal body
        filter_form_modal_size       - bootstrap modal size class (such as modal-lg)
        filter_form_link_title       - text used for the link opening the filter form
        filter_form_tool_tip         - text to use for the tooltip
        filter_form_undo             - include an undo icon to clear applied filters
        filter_form_autocomplete     - autocomplete parameter to use in form tag (on/off)

    example:
        class ListProjects(HandyHelperListPlusFilterView):
            queryset = Project.objects.all()
            title = 'Projects'
            page_description = 'my cool projects'
            table = 'table/table_projects.htm'

            filter_form_obj = ProjectForm
            filter_form_url = '/hostmgr/filter_project/'
            filter_form_title = '<b>Filter Projects: </b><small> </small>'
            filter_form_modal = 'filter_project'
            filter_form_modal_size = 'modal-lg'
            filter_form_modal_backdrop = 'static'
            filter_form_link_title = 'filter project'
            filter_form_tool_tip = 'filter project'
    """
    filter_form = dict()
    filter_form_obj = None
    filter_form_id = None
    filter_form_url = '/handyhelpers/filter_list_view'
    filter_form_title = None
    filter_form_modal = None
    filter_form_modal_backdrop = None
    filter_form_modal_scrollable = False
    filter_form_modal_size = None
    filter_form_link_title = None
    filter_form_tool_tip = None
    filter_form_undo = True
    filter_form_autocomplete = None

    def get(self, request, *args, **kwargs):
        context = dict(base_template=self.base_template, queryset=self.filter_by_query_params(), title=self.title,
                       subtitle=self.page_description, table=self.table, modals=self.modals,
                       add_static=self.add_static, add_template=self.add_template,
                       args=self.args, kwargs=self.kwargs)
        if self.filter_form_obj:
            self.filter_form['form'] = self.filter_form_obj(request.POST or None, initial=self.request.GET.dict())
            self.filter_form['form_id'] = self.filter_form_id
            self.filter_form['action'] = 'Filter'
            self.filter_form['action_url'] = self.filter_form_url
            self.filter_form['title'] = self.filter_form_title
            self.filter_form['modal_name'] = self.filter_form_modal
            self.filter_form['modal_backdrop'] = self.filter_form_modal_backdrop
            self.filter_form['modal_scrollable'] = self.filter_form_modal_scrollable
            self.filter_form['modal_size'] = self.filter_form_modal_size
            self.filter_form['link_title'] = self.filter_form_link_title
            self.filter_form['tool_tip'] = self.filter_form_tool_tip
            self.filter_form['undo'] = self.filter_form_undo
            self.filter_form['autocomplete'] = self.filter_form_autocomplete
            context['filter_form'] = self.filter_form
        return render(request, self.template_name, context)


class HandyHelperListPlusCreateAndFilterView(HandyHelperGenericBaseListView):
    """
    A reusable generic base view to render a ListView where the child view will provide a html table and
    and a create form and a filter form.

    class parameters:
        base_template                - base template used for rendering page;
                                       defaults to: handyhelpers_base.htm
        template_name                - template used when rendering page; defaults to:
                                       handyhelpers/generic/generic_list.html
        args                         - additional args to pass into the template
        kwargs                       - additional kwargs to pass into the template
        queryset                     - queryset to be rendered on the page
        title                        - title to use in template
        page_description             - subtitle to use in template
        table                        - htm file rendering the queryset to be included in the generic_list template
        modals                       - htm file rendering additional modals to be included in the generic_list template
        add_static                   - additional static file to include on the template
        add_template                 - additional template to include on the template
        allow_create_groups          - comma separated list of groups that are allowed to create a new record; used with
                                       InAnyGroup mixin

        create_form_obj              - create form object
        create_form_url              - url the create form (action) should post to
        create_form_title            - title to use on the create form modal (can be html)
        create_form_modal            - name of modal for the create form
        create_form_modal_scrollable - add vertical scrolling to modal body
        create_form_modal_size       - bootstrap modal size class (such as modal-lg)
        create_form_modal_backdrop   - optional data-backdrop value(such as data-backdrop="static")
        create_form_link_title       - text used for the link opening the create form
        create_form_tool_tip         - text to use for the create form link tooltip
        create_form_autocomplete     - autocomplete parameter to use in form tag (on/off)

        filter_form_obj              - filter form object
        filter_form_url              - url the filter form (action) should post to
        filter_form_title            - title to use on the filter form modal (can be html)
        filter_form_modal            - name of modal for the filter form
        filter_form_modal_backdrop   - optional data-backdrop value(such as data-backdrop="static")
        filter_form_modal_scrollable - add vertical scrolling to modal body
        filter_form_modal_size       - bootstrap modal size class (such as modal-lg)
        filter_form_link_title       - text used for the link opening the filter form
        filter_form_tool_tip         - text to use for the filter form link tooltip
        filter_form_undo             - include an undo icon to clear applied filters
        filter_form_autocomplete     - autocomplete parameter to use in form tag (on/off)

    example:
        class ListProjects(HandyHelperBaseCreateListView):
            queryset = Project.objects.all()
            title = 'Projects'
            page_description = 'my cool projects'
            table = 'table/table_projects.htm'

            create_form_obj = ProjectForm
            create_form_url = '/hostmgr/create_project/'
            create_form_title = '<b>Add Project: </b><small> </small>'
            create_form_modal = 'add_project'
            create_form_modal_backdrop = 'static'
            create_form_link_title = 'add project'
            create_form_tool_tip = 'add project'

            filter_form_obj = ProjectForm
            filter_form_url = '/hostmgr/filter_project/'
            filter_form_title = '<b>Filter Projects: </b><small> </small>'
            filter_form_modal = 'filter_projects'
            filter_form_modal_backdrop = 'static'
            filter_form_link_title = 'filter projects'
            filter_form_tool_tip = 'filter projects'
            filter_form_undo = True
    """
    create_form = dict()
    create_form_obj = None
    create_form_url = None
    create_form_title = None
    create_form_modal = None
    create_form_modal_backdrop = None
    create_form_modal_scrollable = False
    create_form_modal_size = None
    create_form_link_title = None
    create_form_tool_tip = None
    create_form_autocomplete = None
    allow_create_groups = None

    filter_form = dict()
    filter_form_obj = None
    filter_form_url = '/handyhelpers/filter_list_view'
    filter_form_title = None
    filter_form_modal = None
    filter_form_modal_backdrop = None
    filter_form_modal_scrollable = False
    filter_form_modal_size = None
    filter_form_link_title = None
    filter_form_tool_tip = None
    filter_form_undo = True
    filter_form_autocomplete = None

    def get(self, request, *args, **kwargs):
        context = dict(base_template=self.base_template, queryset=self.filter_by_query_params(), title=self.title,
                       subtitle=self.page_description, table=self.table, modals=self.modals,
                       add_static=self.add_static, add_template=self.add_template,
                       allow_create_groups=self.allow_create_groups, args=self.args, kwargs=self.kwargs)
        if self.create_form_obj:
            self.create_form['form'] = self.create_form_obj(request.POST or None)
            self.create_form['action'] = 'Add'
            self.create_form['action_url'] = self.create_form_url
            self.create_form['title'] = self.create_form_title
            self.create_form['modal_name'] = self.create_form_modal
            self.create_form['modal_backdrop'] = self.create_form_modal_backdrop
            self.create_form['modal_scrollable'] = self.create_form_modal_scrollable
            self.create_form['modal_size'] = self.create_form_modal_size
            self.create_form['link_title'] = self.create_form_link_title
            self.create_form['tool_tip'] = self.create_form_tool_tip
            self.create_form['autocomplete'] = self.create_form_autocomplete
            context['create_form'] = self.create_form

        if self.filter_form_obj:
            self.filter_form['form'] = self.filter_form_obj(request.POST or None, initial=self.request.GET.dict())
            self.filter_form['action'] = 'Filter'
            self.filter_form['action_url'] = self.filter_form_url
            self.filter_form['title'] = self.filter_form_title
            self.filter_form['modal_name'] = self.filter_form_modal
            self.filter_form['modal_backdrop'] = self.filter_form_modal_backdrop
            self.filter_form['modal_scrollable'] = self.filter_form_modal_scrollable
            self.filter_form['modal_size'] = self.filter_form_modal_size
            self.filter_form['link_title'] = self.filter_form_link_title
            self.filter_form['tool_tip'] = self.filter_form_tool_tip
            self.filter_form['undo'] = self.filter_form_undo
            self.filter_form['autocomplete'] = self.filter_form_autocomplete
            context['filter_form'] = self.filter_form

        return render(request, self.template_name, context)


class HandyHelperPaginatedListView(HandyHelperGenericBaseListView):
    """
    A reusable generic base view to render a ListView with pagination where the child view will provide a html table.

    class parameters:
        base_template       - base template used for rendering page; defaults to: handyhelpers_base.htm
        template_name       - template used when rendering page; defaults to: handyhelpers/generic/generic_list.html
        args                - additional args to pass into the template
        kwargs              - additional kwargs to pass into the template
        queryset            - queryset to be rendered on the page
        title               - title to use in template
        page_description    - subtitle to use in template
        table               - htm file rendering the queryset to be included in the generic_list template
        modals              - htm file rendering additional modals to be included in the generic_list template
        add_static          - additional static file to include on the template
        add_template        - additional template to include on the template
        allow_create_groups - comma separated list of groups that are allowed to create a new record; used with
                              InAnyGroup mixin

        paginate_by         - number of objects to list per page; defaults to 10
        elided_on_each_side - number of pages to show on either side of an ellipsis
        elided_on_ends      - number of pages to show on ends when ellipsis is present
        include_total       - display the total number of objects on the page (below pagination controls)

        create_form_obj            - create form object
        create_form_url            - url the create form (action) should post to
        create_form_title          - title to use on the create form modal (can be html)
        create_form_modal_backdrop - optional data-backdrop value(such as data-backdrop="static")
        create_form_modal_name     - name of modal for the create form
        create_form_modal_size     - bootstrap modal size class (such as modal-lg)
        create_form_link_title     - text used for the link opening the create form
        create_form_tool_tip       - text to use for the create form link tooltip
        create_form_autocomplete   - autocomplete parameter to use in form tag (on/off)

        filter_form_obj            - filter form object
        filter_form_url            - url the form (action) should post to
        filter_form_title          - title to use on the filter form modal (can be html)
        filter_form_modal_backdrop - optional data-backdrop value(such as data-backdrop="static")
        filter_form_modal_name     - name of modal for the filter form
        filter_form_modal_size     - bootstrap modal size class (such as modal-lg)
        filter_form_link_title     - text used for the link opening the filter form
        filter_form_tool_tip       - text to use for the tooltip
        filter_form_undo           - include an undo icon to clear applied filters
        filter_form_autocomplete   - autocomplete parameter to use in form tag (on/off)

    example:
        class ListProjects(HandyHelperPaginatedListView):
            queryset = Project.objects.all()
            title = 'Projects'
            page_description = 'my cool projects'
            table = 'table/table_projects.htm'
            modals = 'project_modals.htm'
    """
    paginate_by = 10
    elided_on_each_side = 1
    elided_on_ends = 1
    include_total = True
    template_name = 'handyhelpers/generic/generic_paginated_list.html'

    create_form = dict()
    create_form_obj = None
    create_form_url = None
    create_form_title = None
    create_form_modal_name = None
    create_form_modal_backdrop = None
    create_form_modal_scrollable = False
    create_form_modal_size = None
    create_form_link_title = None
    create_form_tool_tip = None
    create_form_autocomplete = None
    allow_create_groups = None

    filter_form = dict()
    filter_form_obj = None
    filter_form_id = None
    filter_form_url = '/handyhelpers/filter_list_view'
    filter_form_title = None
    filter_form_modal_name = None
    filter_form_modal_backdrop = None
    filter_form_modal_scrollable = False
    filter_form_modal_size = None
    filter_form_link_title = None
    filter_form_tool_tip = None
    filter_form_undo = True
    filter_form_autocomplete = None

    def get(self, request, *args, **kwargs):
        try:
            page = int(request.GET.get('page', 1))
        except ValueError:
            page = 1
        paginator = Paginator(self.filter_by_query_params(), per_page=self.paginate_by)
        if page > paginator.num_pages:
            page = paginator.num_pages
        page_object = paginator.get_page(page)
        page_object.adjusted_elided_pages = paginator.get_elided_page_range(page,
                                                                            on_each_side=self.elided_on_each_side,
                                                                            on_ends=self.elided_on_ends)
        context = dict(base_template=self.base_template, page_obj=page_object, include_total=self.include_total,
                       queryset=page_object, title=self.title, subtitle=self.page_description, table=self.table,
                       modals=self.modals, add_static=self.add_static, add_template=self.add_template,
                       args=self.args, kwargs=self.kwargs)

        if self.create_form_obj:
            self.create_form['form'] = self.create_form_obj(request.POST or None)
            self.create_form['action'] = 'Add'
            self.create_form['action_url'] = self.create_form_url
            self.create_form['title'] = self.create_form_title
            self.create_form['modal_backdrop'] = self.create_form_modal_backdrop
            self.create_form['modal_name'] = self.create_form_modal_name
            self.create_form['modal_scrollable'] = self.create_form_modal_scrollable
            self.create_form['modal_size'] = self.create_form_modal_size
            self.create_form['link_title'] = self.create_form_link_title
            self.create_form['tool_tip'] = self.create_form_tool_tip
            self.create_form['autocomplete'] = self.create_form_autocomplete
            context['create_form'] = self.create_form

        if self.filter_form_obj:
            self.filter_form['form'] = self.filter_form_obj(request.POST or None, initial=self.request.GET.dict())
            self.filter_form['form_id'] = self.filter_form_id
            self.filter_form['action'] = 'Filter'
            self.filter_form['action_url'] = self.filter_form_url
            self.filter_form['title'] = self.filter_form_title
            self.filter_form['modal_backdrop'] = self.filter_form_modal_backdrop
            self.filter_form['modal_name'] = self.filter_form_modal_name
            self.filter_form['modal_scrollable'] = self.filter_form_modal_scrollable
            self.filter_form['modal_size'] = self.filter_form_modal_size
            self.filter_form['link_title'] = self.filter_form_link_title
            self.filter_form['tool_tip'] = self.filter_form_tool_tip
            self.filter_form['undo'] = self.filter_form_undo
            self.filter_form['autocomplete'] = self.filter_form_autocomplete
            context['filter_form'] = self.filter_form
        return render(request, self.template_name, context)
