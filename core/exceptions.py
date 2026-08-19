import logging

from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """Tüm DRF hatalarını tutarlı bir `{"detail": ..., "errors": ...}` gövdesiyle döndürür."""
    response = exception_handler(exc, context)

    if response is None:
        logger.exception("Unhandled exception in %s", context['view'].__class__.__name__, exc_info=exc)
        return response

    data = response.data
    if isinstance(data, dict) and 'detail' in data and len(data) == 1:
        response.data = {'detail': data['detail']}
    else:
        detail = data.get('detail') if isinstance(data, dict) else None
        response.data = {
            'detail': detail or 'Doğrulama hatası oluştu.',
            'errors': data,
        }

    logger.warning(
        "%s in %s: %s",
        exc.__class__.__name__,
        context['view'].__class__.__name__,
        response.data,
    )

    return response
