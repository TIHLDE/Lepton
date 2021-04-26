from app.common.serializers import BaseModelSerializer

from ..models import Category


class CategorySerializer(BaseModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"  # bad form
