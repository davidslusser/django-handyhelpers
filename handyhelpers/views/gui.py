from django.conf import settings
from django.shortcuts import render
from django.views.generic import ListView, View

from handyhelpers.mixins.view_mixins import FilterByQueryParamsMixin


class HandyHelperGenericBaseView(View):
    """ Generic view used to set the base_template variable. This extends django.view.generic.View and will use the base
     template defined in the BASE_TEMPLATE settings variable or use handyhelpers/handyhelpers_base.htm if not provided.

    class parameters:
        base_template - base template used for rendering page; defaults to: handyhelpers_base.htm
        args          - additional args to pass into the template
        kwargs        - additional kwargs to pass into the template
    """
    base_template = getattr(settings, 'BASE_TEMPLATE', 'handyhelpers/handyhelpers_base.htm')
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
    handyhelpers/handyhelpers_base.htm if not provided. This view also includes the
    handyhelpers.mixins.view_mixins.FilterByQueryParamsMixin mixin to allow filtering by query parameters.

    class parameters:
        base_template - base template used for rendering page; defaults to: handyhelpers_base.htm
        template_name - template used when rendering page; defaults to: handyhelpers/generic/generic_list.html
        title         - title to use in template
        table         - htm file rendering the queryset to be included in the generic_list template
        modals        - htm file rendering additional modals to be included in the generic_list template
    """
    base_template = getattr(settings, 'BASE_TEMPLATE', 'handyhelpers/handyhelpers_base.htm')
    template = 'handyhelpers/generic/generic_list.html'
    title = None
    table = None
    modals = None
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
    template_name = 'handyhelpers/generic/generic_index.html'

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
        template_name        - template used when rendering page; defaults to: handyhelpers/generic/generic_action.html
        title                - page title to use; will display in a H1 element
        subtitle             - subtitle to use; will display in a H5 element (None if not provided)
        item_list            - list of items/actions to display (one per card)
        protected_item_list  - list of items/action only visible to members of protected_group_name
        protected_group_name - name of group to show protected_item_list items to
        form_list            - list of django forms used in page
    """
    template_name = 'handyhelpers/generic/generic_action.html'
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
    template = 'handyhelpers/generic/generic_about.html'
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
        return render(request, self.template, context)


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
                       sub_title=self.page_description, table=self.table, modals=self.modals,
                       args=self.args, kwargs=self.kwargs)
        return render(request, self.template, context)


class HandyHelperBaseListView(HandyHelperListView):
    """ maintaining the HandyHelperBaseListView for legacy compatibility """
    pass


class HandyHelperListPlusCreateView(HandyHelperGenericBaseListView):
    """
    A reusable generic base view to render a ListView where the child view will provide a html table and create form.

    class parameters:
        base_template          - base template used for rendering page; defaults to: handyhelpers_base.htm
        template_name          - template used when rendering page; defaults to: handyhelpers/generic/generic_list.html
        args                   - additional args to pass into the template
        kwargs                 - additional kwargs to pass into the template
        queryset               - queryset to be rendered on the page
        title                  - title to use in template
        page_description       - subtitle to use in template
        table                  - htm file rendering the queryset to be included in the generic_list template
        modals                 - htm file rendering additional modals to be included in the generic_list template
        create_form_obj        - form object
        create_form_url        - url the form (action) should post to
        create_form_title      - title to use on the create form modal (can be html)
        create_form_modal      - name of modal for the create form
        create_form_link_title - text used for the link opening the create form

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
            create_form_link_title = 'add project'
    """
    create_form = dict()
    create_form_obj = None
    create_form_url = None
    create_form_title = None
    create_form_modal = None
    create_form_link_title = None

    def get(self, request, *args, **kwargs):
        context = dict(base_template=self.base_template, queryset=self.filter_by_query_params(), title=self.title,
                       sub_title=self.page_description, table=self.table, modals=self.modals,
                       args=self.args, kwargs=self.kwargs)
        if self.create_form_obj:
            self.create_form['form'] = self.create_form_obj(request.user.username, request.POST or None)
            self.create_form['action'] = 'Add'
            self.create_form['action_url'] = self.create_form_url
            self.create_form['title'] = self.create_form_title
            self.create_form['modal_name'] = self.create_form_modal
            self.create_form['link_title'] = self.create_form_link_title
            context['create_form'] = self.create_form
        return render(request, self.template, context)


class HandyHelperBaseListPlusCreateView(HandyHelperListView):
    """ maintaining the HandyHelperBaseListPlusCreateView for legacy compatibility """
    pass
