from rest_framework import status
from rest_framework.exceptions import APIException


class VippsCallbackInternalServerException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Det skjedde en feil med oppdatering av Vipps betalingsstatus fra Vipps callback."


class VippsForcePaymentException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = (
        "Det skjedde en feil med tvungen oppdatering av Vipps betalingsstatus."
    )
