from django.conf import settings
from django.shortcuts import render
from django.views.generic import ListView, View

from djangohelpers.mixins.view_mixins import FilterByQueryParamsMixin


class HandyHelperBaseListView(FilterByQueryParamsMixin, ListView):
    """ base view for CBV list pages

    class parameters:
         queryset - queryset to be rendered on the page
         title - title to use in template
         page_description - subtitle to use in template
         table - htm file rendering the queryset to be included in the generic_list template
         modals - htm file rendering additional modals to be included in the generic_list template

    example:
        class ListProjects(HandyHelperBaseListView):
            queryset = Project.objects.all()
            title = "Projects"
            page_description = "my cool projects"
            table = "table/table_projects.htm"
            modals = "project_modals.htm"
    """
    base_template = settings.BASE_TEMPLATE
    template = "handyhelpers/generic/generic_list.html"
    title = None
    table = None
    modals = None

    def get(self, request, *args, **kwargs):
        context = dict()
        template = self.template
        context['base_template'] = self.base_template
        context['queryset'] = self.filter_by_query_params()
        context['title'] = self.title
        context['sub_title'] = self.page_description
        context['table'] = self.table
        context['modals'] = self.modals
        return render(request, template, context=context)


class HandyHelperBaseCreateListView(FilterByQueryParamsMixin, ListView):
    """ base view for CBV list pages that include create form

    class parameters:
        queryset - queryset to be rendered on the page
        title - title to use in template
        page_description - subtitle to use in template
        table - htm file rendering the queryset to be included in the generic_list template
        modals - htm file rendering additional modals to be included in the generic_list template
        create_form_obj = form object
        create_form_url = url the form (action) should post to
        create_form_title = title to use on the create form (can be html)
        create_form_modal = name of modal for the create form
        create_form_link_title = text used for the link opening the create form

    example:
        class ListProjects(HandyHelperBaseCreateListView):
            queryset = Project.objects.all()
            title = "Projects"
            page_description = "my cool projects"
            table = "table/table_projects.htm"
            create_form_obj = ProjectForm
            create_form_url = '/hostmgr/create_project/'
            create_form_title = "<b>Add Project: </b><small> </small>"
            create_form_modal = "add_project"
            create_form_link_title = "add project"
    """
    base_template = settings.BASE_TEMPLATE
    template = "handyhelpers/generic/generic_list.html"
    title = None
    table = None
    modals = None
    create_form = dict()
    create_form_obj = None
    create_form_url = None
    create_form_title = None
    create_form_modal = None
    create_form_link_title = None

    def get(self, request, *args, **kwargs):
        context = dict()
        template = self.template
        context['base_template'] = self.base_template
        context['queryset'] = self.filter_by_query_params()
        context['title'] = self.title
        context['sub_title'] = self.page_description
        context['table'] = self.table
        context['modals'] = self.modals
        if self.create_form_obj:
            self.create_form['form'] = self.create_form_obj(request.user.username, request.POST or None)
            self.create_form['action'] = "Add"
            self.create_form['action_url'] = self.create_form_url
            self.create_form['title'] = self.create_form_title
            self.create_form['modal_name'] = self.create_form_modal
            self.create_form['link_title'] = self.create_form_link_title
            context['create_form'] = self.create_form
        return render(request, template, context=context)


class HandyHelperAboutView(View):
    """
    Generic view to render an 'about' page.

    class parameters:
        title    - page title to use ('About' if not provided)
        subtitle - subtitle to use (None if not provided)
        version  - version to display (None if not provided)
        details  - any specific details to display (None if not provided)
        source   - link to source code repository (None if not provided)
        contact  - any desired contact information (None if not provided)
        links    - list of dictionary containing links; ex. [{'some reference': 'www.somewebsite.com}, ...]
    """
    base_template = settings.BASE_TEMPLATE
    template = "handyhelpers/generic/generic_about.html"
    title = "About"
    subtitle = None
    version = None
    details = None
    source = None
    contact = None
    links = []

    def get(self, request, *args, **kwargs):
        context = dict()
        template = self.template
        context['base_template'] = self.base_template
        context['title'] = self.title
        context['subtitle'] = self.subtitle
        context['version'] = self.version
        context['details'] = self.details
        context['source'] = self.source
        context['contact'] = self.contact
        context['links'] = self.links
        return render(request, template, context=context)
