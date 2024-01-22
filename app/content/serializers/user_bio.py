from rest_framework import serializers
from .models import UserBio

class UserBioSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserBio
        fields = [
            'role',
            'description',
            'gitHub_link',
            'linkedIn_link'
        ]