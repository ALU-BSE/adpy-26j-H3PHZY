from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .models import GlassLog
from django.utils import timezone
from django.apps import apps


SENSITIVE_PREFIXES = getattr(settings, 'SENSITIVE_PATH_PREFIXES', [
    '/api/shipments',
    '/api/international',
    '/api/users',
    '/api/identity',
])


class GlassLogMiddleware(MiddlewareMixin):
    """Log sensitive GET accesses automatically.

    - only handles GET requests
    - checks path prefix against SENSITIVE_PREFIXES
    - tries to resolve model/object when possible
    """

    def process_request(self, request):
        # Only interested in GETs
        if request.method != 'GET':
            return None

        path = request.path

        # Quick prefix check
        if not any(path.startswith(p) for p in SENSITIVE_PREFIXES):
            return None

        # Try to resolve view kwargs to find an object pk
        try:
            resolver_match = resolve(path)
            kwargs = resolver_match.kwargs
        except Exception:
            kwargs = {}

        app_label = ''
        model_name = ''
        object_pk = ''

        # Common lookup keys
        pk_keys = ['pk', 'id', 'tracking_number']
        found_pk = None
        for k in pk_keys:
            if k in kwargs:
                found_pk = kwargs[k]
                break

        # Try to infer model by URL namespace or path
        # Simple mapping: shipments -> domestic.Shipment or international.InternationalShipment
        Model = None
        try:
            if path.startswith('/api/shipments'):
                Model = apps.get_model('domestic', 'Shipment')
            elif path.startswith('/api/international'):
                Model = apps.get_model('international', 'InternationalShipment')
            elif path.startswith('/api/users'):
                parts = settings.AUTH_USER_MODEL.split('.')
                Model = apps.get_model(parts[0], parts[1])
        except Exception:
            Model = None

        if Model and found_pk is not None:
            # attempt to fetch object
            try:
                obj = None
                # try common field lookups
                if hasattr(Model, 'objects'):
                    if 'tracking_number' in [f.name for f in Model._meta.fields]:
                        obj = Model.objects.filter(tracking_number=found_pk).first()
                    else:
                        obj = Model.objects.filter(pk=found_pk).first()

                if obj is not None:
                    app_label = obj._meta.app_label
                    model_name = obj._meta.model_name
                    object_pk = str(getattr(obj, obj._meta.pk.name))
            except Exception:
                pass

        # Create log entry (non-blocking simple write)
        try:
            GlassLog.objects.create(
                user=(request.user if getattr(request, 'user', None) and request.user.is_authenticated else None),
                method=request.method,
                path=path,
                app_label=app_label or '',
                model_name=model_name or '',
                object_pk=object_pk or '',
                extra={'params': dict(request.GET)} if request.GET else None,
            )
        except Exception:
            # don't fail the request if logging fails
            pass

        return None
