import json

from django.views import View
from django.http import HttpResponse


class AjaxGetView(View):
    """ generic view for handling GET requests sent via ajax """
    template = None
    data = {}

    def get(self, request, *args, **kwargs):
        try:
            if not self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return HttpResponse('Invalid request', status=400)    
            if 'client_response' in self.request.GET:
                return HttpResponse(json.dumps({'server_response': self.template.render({'data': self.data})}),
                                    content_type='application/javascript')
            return HttpResponse('Invalid request inputs', status=400)
        except Exception:
            return HttpResponse(json.dumps({'server_response': self.template.render({'data': None})}),
                                    content_type='application/javascript')
