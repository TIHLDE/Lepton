from app.graphql.generics import GenericQuery
from app.graphql.mixins import ListModelMixin, RetrieveModelMixin


class ModelQuery(RetrieveModelMixin, ListModelMixin, GenericQuery):
    pass
