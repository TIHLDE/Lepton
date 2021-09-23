from app.graphql_core.generics import GenericQuery
from app.graphql_core.mixins import ListModelMixin, RetrieveModelMixin


class ModelQuery(RetrieveModelMixin, ListModelMixin, GenericQuery):
    pass
