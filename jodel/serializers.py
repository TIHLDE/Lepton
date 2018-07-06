#!/usr/bin/env python

from rest_framework import serializers
from .models import Jodel

class JodelSerializer(serializers.HyperlinkedModelSerializer):
#class JodelSerializer(serializers.Serializer):
    class Meta:
        model = Jodel
        fields = ('text', 'votes', 'creation_time')
