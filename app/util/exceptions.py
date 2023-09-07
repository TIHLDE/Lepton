import logging
import traceback

from django.conf import settings
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if not response and isinstance(exc, IntegrityError) and not settings.DEBUG:
        response = Response(
            {"detail": "Some values are supposed to be unique but are not."},
            status=status.HTTP_409_CONFLICT,
        )

    if response:
        log_api_error(response, exc)
    else:
        logger.error(f"Unhandled request exception: {traceback(exc)}")

    if not settings.DEBUG and not response:
        response = Response(
            {"detail": "Noe gikk alvorlig galt da vi behandlet forespørselen din"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


def log_api_error(response, exc):
    detail = None
    if isinstance(response.data, dict):
        detail = response.data.get("detail", None)

    logger.warning(
        f"Request error: status={response.status_code}, detail={detail}, exc={exc}"
    )
