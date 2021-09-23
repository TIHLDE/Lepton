from app.graphql_core.generics import GenericMutation, GenericQuery
from app.graphql_core.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)


class ModelQuery(RetrieveModelMixin, ListModelMixin, GenericQuery):
    pass


class ModelMutation(CreateModelMixin, GenericMutation):
    pass
