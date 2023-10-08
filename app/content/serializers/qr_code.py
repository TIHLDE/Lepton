import qrcode

from io import BytesIO

from django.core.files import File

from rest_framework import serializers

from app.content.models import QRCode
from app.common.serializers import BaseModelSerializer
from app.common.azure_file_handler import AzureFileHandler


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = (
            "id",
            "name",
            "url",
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

        qr = qrcode.QRCode(
            version=1,
            box_size=3,
            border=3
        )
        qr.add_data(url)
        qr.make(fit=True)
    
        img = qr.make_image(fill='black', back_color='white')
        img_byte_arr = BytesIO()
        # convert to png file
        img.save(img_byte_arr, 'PNG')
        qr_code_image = File(img_byte_arr, name='qr.png')

        print(qr_code_image.size)
        
        image_url = AzureFileHandler(qr_code_image).uploadBlob("img/png")
        validated_data["image"] = image_url

        return super().create(validated_data)
