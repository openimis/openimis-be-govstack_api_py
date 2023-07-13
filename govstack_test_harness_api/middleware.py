from django.http import HttpResponse
from django.conf import settings
from django.apps import apps


class InformationMediatorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        config = apps.get_app_config('govstack_test_harness_api')
        im_client = config.IM_CLIENT
        im_header = request.META.get('HTTP_INFORMATION_MEDIATOR_CLIENT')
        if im_header != im_client:
            return HttpResponse('Unauthorized', status=401)
        return self.get_response(request)
