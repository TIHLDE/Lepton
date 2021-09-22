import logging

from django.conf import settings
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if not response and isinstance(exc, IntegrityError):
        response = Response(
            {"detail": "Some values are supposed to be unique but are not."},
            status=status.HTTP_409_CONFLICT,
        )

    if not settings.DEBUG and not response:
        message = (
            str(exc)
            if exc
            else "Noe gikk alvorlig galt da vi behandlet forespørselen din "
        )
        response = Response(
            {"detail": message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if response:
        log_api_error(response, exc)
    else:
        logger.error(f"Unhandled request exception: {exc}")
    return response


def log_api_error(response, exc):
    detail = None
    if isinstance(response.data, dict):
        detail = response.data.get("detail", None)

    logger.warning(
        f"Request error: status={response.status_code}, detail={detail}, exc={exc}"
    )
