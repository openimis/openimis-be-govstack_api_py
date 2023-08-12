from functools import wraps

from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from govstack_api.building_blocks.bb_digital_registries.registries.base_registry import MutationError


def handle_mutation_exceptions():
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            try:
                return view_func(self, request, *args, **kwargs)
            except MutationError as e:
                return Response(e.detail, 400)
            except ValidationError as e:
                return Response(e.detail, status=e.status_code)
        return wrapper
    return decorator
