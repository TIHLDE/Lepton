from rest_framework import serializers
from app.wrapped.util.statistics_util import calculate_statistics
from app.content.models.user import User


class StatisticsSerializer(serializers.Serializer):
    year = serializers.IntegerField()

    # FIXME - We don't want to use a model if it is not strictly nescessary?
    class Meta:
        model = User


"""
class StatisticsCreateSerializer(serializers.Serializer):
    year = serializers.IntegerField()

    def create(self, validated_data, **kwargs):
        user = self.context["request"].user
        print("USER: ", user)
        year = validated_data.pop("year")
        stats = calculate_statistics(user, year)
        return stats
"""
