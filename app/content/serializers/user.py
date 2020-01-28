from rest_framework import serializers

from ..models import User, UserEvent
from .event import EventInUserSerializer

from django.contrib.auth.hashers import make_password



class UserSerializer(serializers.ModelSerializer):
	events = serializers.SerializerMethodField()
	groups = serializers.SerializerMethodField()

	class Meta:
		model = User
		fields = (
			'user_id',
			'first_name',
			'last_name',
			'email',
			'cell',
			'em_nr',
			'home_busstop',
			'gender',
			'user_class',
			'user_study',
			'allergy',
			'tool',
			'events',
			'groups'
		)

	def get_events(self, obj):
		""" Lists all events user is to attend or has attended """
		user_events = UserEvent.objects.filter(user__user_id=obj.user_id).order_by('event__start_date')
		events = [user_event.event for user_event in user_events if not user_event.event.expired]
		return EventInUserSerializer(events, many=True).data

	def get_groups(self, obj):
		""" Lists all groups a user is a member of """
		return [group.name for group in obj.groups.all()]


class UserMemberSerializer(UserSerializer):
	"""Serializer for user update to prevent them from updating extra_kwargs fields"""
	class Meta(UserSerializer.Meta):
		fields = UserSerializer.Meta.fields
		read_only_fields = ('user_id', 'first_name', 'last_name', 'email',)

class UserCreateSerializer(serializers.ModelSerializer):
	"""Serializer for creating user """
	class Meta:
			model = User
			fields = (
			'user_id',
			'password',
			'first_name',
			'last_name',
			'email',
			'user_class',
			'user_study',
			)

	def create(self, validated_data):
		user = User.objects.create(
			user_id=validated_data['user_id'],
			password = make_password(validated_data['password']),
			first_name=validated_data['first_name'],
			last_name=validated_data['last_name'],
			email=validated_data['email'],
			user_class=validated_data['user_class'],
			user_study=validated_data['user_study'],
		)
		user.set_password(validated_data['password'])
		user.save()
		return user
