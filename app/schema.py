import graphene
from enumchoicefield import EnumChoiceField
from graphene_django.converter import convert_django_field


@convert_django_field.register(EnumChoiceField)
def my_convert_function(field, registry=None):
    # Customization here
    return graphene.String()


import app.forms.schema  # noqa E402


# TODO: move to new app 'api'
class Query(
    app.forms.schema.Query, graphene.ObjectType,
):
    class Meta:
        pass


class Mutation(
    app.forms.schema.Mutation, graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
