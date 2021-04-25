import logging

from rest_framework import status, viewsets
from rest_framework.response import Response
from app.common.permissions import IsMember

from app.payment.util.refund_form_mail import (
    UnsupportedFileException,
    create_pdf,
    data_is_valid,
    format_image_data,
    send_refund_mail,
)


class RefundFormViewSet(viewsets.ModelViewSet):
    permission_classes = (IsMember,)
    queryset = None

    def create(self, request):
        data = request.data.copy()
        try:
            req_fields = data_is_valid(data)
            if len(req_fields) > 0:
                return Response(
                    f'Required fields {", ".join(req_fields)}',
                    status=status.HTTP_400_BAD_REQUEST,
                )
            data = format_image_data(data)
            file = create_pdf(data)
            send_refund_mail(data, file)
            return Response(
                "Receipt is generated and sent to the group's cashier!",
                status=status.HTTP_200_OK,
            )
        except UnsupportedFileException:
            return Response(
                """One of the file types are not supported.
                Use PNG, JPEG, GIF, HEIC or PDF""",
                status=status.HTTP_400_BAD_REQUEST,
            )
        except RuntimeError as e:
            logging.exception(e)
            return Response(
                "Could not generate PDF", status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                f"Something unexpected happened. {e}",
                status=status.HTTP_400_BAD_REQUEST,
            )
