from django.http import Http404

import graphene
from graphene_django.rest_framework.mutation import SerializerMutation

from app.content.serializers import NewsSerializer
from app.content.types import NewsType
from app.content.views import NewsViewSet


class NewsMutation(SerializerMutation):
    class Meta:
        serializer_class = NewsSerializer
        model_operations = ["create", "update"]
        lookup_field = "id"

    news = graphene.Field(NewsType)

    @classmethod
    def __create_view(cls, info, **kwargs):
        view = NewsViewSet()
        view.kwargs = kwargs
        view.action_map = {"put": "update"}  # TODO: pass as parameter
        view.request = view.initialize_request(info.context, *(), **kwargs)
        view.check_permissions(view.request)
        return view

    @classmethod
    def get_serializer_kwargs(cls, root, info, **kwargs):
        cls.__create_view(info, **kwargs)
        if "id" in kwargs:
            view = cls.__create_view(info, **kwargs)
            instance = view.get_object()
            if instance:
                return {"instance": instance, "data": kwargs, "partial": True}
            else:
                raise Http404("Question does not exist")

        return {"data": kwargs, "partial": False}
