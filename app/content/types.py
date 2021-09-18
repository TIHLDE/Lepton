from graphene_django import DjangoObjectType

from app.content.models import User
from app.content.models.news import News


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"  # TODO: bad form


class NewsType(DjangoObjectType):
    class Meta:
        model = News
        fields = "__all__"  # TODO: bad form
