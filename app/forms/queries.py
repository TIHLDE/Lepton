import graphene

from app.forms.models import Form
from app.forms.types import FormUnionType
from app.graphql.permissions import DRYGraphQLPermissions
from app.graphql.queries import ModelQuery


class FormQuery(ModelQuery):
    lookup_field = "id"
    queryset = Form.objects.all()
    permission_classes = [DRYGraphQLPermissions]

    forms = graphene.List(FormUnionType)
    form = graphene.Field(FormUnionType, id=graphene.UUID())

    @classmethod
    def resolve_forms(cls, root, info, **kwargs):
        return super().resolve_list(root, info, **kwargs)

    @classmethod
    def resolve_form(cls, root, info, id, **kwargs):
        return super().resolve_retrieve(root, info, id=id)
