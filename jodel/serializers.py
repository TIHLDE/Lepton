#!/usr/bin/env python

from rest_framework import serializers
from .models import Jodel, Comment

class CommentSerializer(serializers.HyperlinkedModelSerializer):
    voteState = serializers.ReadOnlyField()

    """A jodel comment"""
    class Meta:
        model = Comment
        fields = ('id', 'parent', 'text', 'votes', 'time', 'voteState')
        abstract = True

class JodelSerializer(serializers.HyperlinkedModelSerializer):
    """Serializes Jodels without comments"""
    voteState = serializers.ReadOnlyField()

    class Meta:
        model = Jodel
        fields = ('id', 'text', 'votes', 'time', 'voteState')
        abstract = True

class JodelWithCommentsSerializer(serializers.HyperlinkedModelSerializer):
    """Serializes with all comments"""
    voteState = serializers.ReadOnlyField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Jodel
        fields = ('id', 'text', 'votes', 'time', 'voteState', 'comments')
        abstract = True
