import re

from django.core.exceptions import ValidationError

from app.common.serializers import BaseModelSerializer
from app.content.models import ShortLink


class ShortLinkSerializer(BaseModelSerializer):
    class Meta:
        model = ShortLink
        fields = ["name", "url"]

    def validate_name(self, data):
        regex = re.compile("^(a/.*|k/.*|n/.*|(om/.*)|a|k|n|om)$", re.IGNORECASE)
        if regex.match(data):
            raise ValidationError(
                "Dette navnet er reservert. Navn som starter med 'om/', 'a/', 'k/' og 'n/' er ikke tilgjengelige."
            )
        return data
