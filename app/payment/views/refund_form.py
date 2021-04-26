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
        data["mailfrom"] = request.user.email
        try:
            req_fields = data_is_valid(data)
            if len(req_fields):
                return Response(
                    f'Påkrevde felt {", ".join(req_fields)}',
                    status=status.HTTP_400_BAD_REQUEST,
                )
            data = format_image_data(data)
            file = create_pdf(data)
            send_refund_mail(data, file)
            return Response(
                {"details": "Kvittering er generert og sendt til økonomi ansvarlig!"},
                status=status.HTTP_200_OK,
            )
        except UnsupportedFileException:
            return Response(
                {
                    "details": """En eller flere filer er ikke støttet.
                Bruk PNG, JPEG, GIF, HEIC or PDF"""
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except RuntimeError as e:
            logging.exception(e)
            return Response(
                {"details": "Kunne ikke generere PDF"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logging.exception(e)
            return Response(
                {"details": "Noe uventet skjedde"}, status=status.HTTP_400_BAD_REQUEST,
            )
