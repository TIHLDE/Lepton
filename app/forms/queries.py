import graphene

from app.forms.models import Form
from app.forms.types import FormUnionType
from app.graphql_core.generics import DRYGraphQLPermissions
from app.graphql_core.queries import ModelQuery


class FormQuery(ModelQuery):
    queryset = Form.objects.all()
    permission_classes = [DRYGraphQLPermissions]
    lookup_field = "id"

    forms = graphene.List(FormUnionType)
    form = graphene.Field(FormUnionType, id=graphene.UUID())

    @classmethod
    def resolve_forms(cls, root, info, **kwargs):
        return super().resolve_list(root, info, **kwargs)

    @classmethod
    def resolve_form(cls, root, info, id, **kwargs):
        return super().resolve_retrieve(root, info, id=id)
