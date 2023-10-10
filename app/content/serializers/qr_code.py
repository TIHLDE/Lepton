import qrcode
import os

from django.core.files import File

from rest_framework import serializers

from app.content.models import QRCode
from app.content.util.byte_file import ByteFile
from app.common.serializers import BaseModelSerializer
from app.common.azure_file_handler import AzureFileHandler


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = (
            "id",
            "name",
            "created_at",
            "updated_at",
            "image"
        )


class QRCodeCreateSerializer(BaseModelSerializer):
    class Meta:
        model = QRCode
        fields = (
            "name",
            "url",
            "user"
        )
    
    def create(self, validated_data):
        url = validated_data.pop("url")
        name = validated_data.pop("name")

        image_url = self.create_qr(url, name)
        os.remove("qr.png")

        validated_data["image"] = image_url

        return super().create(validated_data)
    
    def create_qr(self, url, name):
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=4
        )

        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")
        img.save("qr.png")

        with open(file="qr.png", mode="rb") as data:
            file = ByteFile(
                data=data,
                content_type="image/png",
                size=File(data).size,
                name=name
            )
            return AzureFileHandler(file).uploadBlob()         
