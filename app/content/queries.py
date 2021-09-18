import graphene

from app.content.types import NewsType, UserType
from app.content.views import NewsViewSet, UserViewSet
from app.util.queries import BaseQuery


class NewsQuery(BaseQuery):
    view = NewsViewSet

    news = graphene.Field(NewsType, id=graphene.String(required=True))
    all_news = graphene.List(NewsType)

    @classmethod
    def resolve_all_news(cls, root, info, **kwargs):
        return super().resolve_list(info, **kwargs)

    @classmethod
    def resolve_news(cls, root, info, **kwargs):
        return super().resolve_retrieve(info, **kwargs)


class UserQuery(BaseQuery):
    view = UserViewSet

    users = graphene.Field(UserType)
