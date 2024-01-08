from rest_framework import serializers
from app.wrapped.util.statistics_util import calculate_statistics


class StatisticsSerializer(serializers.Serializer):
    year = serializers.IntegerField()

    class Meta:
        pass


class StatisticsGetSerializer(serializers.Serializer):
    year = serializers.IntegerField()

    class Meta:
        pass

    def create(self, validated_data, **kwargs):
        user = self.context["request"].user
        print("USER: ", user)
        year = validated_data.pop("year")
        stats = calculate_statistics(user, year)
        return stats
