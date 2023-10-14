import os

from django.core.files import File
from rest_framework import serializers

import qrcode

from app.common.azure_file_handler import AzureFileHandler
from app.common.serializers import BaseModelSerializer
from app.content.models import QRCode
from app.content.util.byte_file import ByteFile


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = ("id", "name", "created_at", "updated_at", "image")


class QRCodeCreateSerializer(BaseModelSerializer):
    class Meta:
        model = QRCode
        fields = (
            "name",
            "url",
        )

    def create(self, validated_data):
        url = validated_data.pop("url")
        name = validated_data.pop("name")
        user = validated_data.pop("user")

        image_url = self.create_qr(url, name)

        qr_code = QRCode.objects.create(user=user, name=name, url=url, image=image_url)

        return qr_code

    def create_qr(self, url, name):
        SAVE_PATH = "qr.png"

        qr = qrcode.QRCode(version=1, box_size=10, border=4)

        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")
        img.save(SAVE_PATH)

        with open(file=SAVE_PATH, mode="rb") as data:
            file = ByteFile(
                data=data, content_type="image/png", size=File(data).size, name=name
            )
            url = AzureFileHandler(file).uploadBlob()

        os.remove(SAVE_PATH)
        return url
