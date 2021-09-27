from graphene.types.mutation import MutationOptions


class ModelOptions(MutationOptions):
    lookup_field = "pk"
    serializer_class = None
    permissions = []
    queryset = None


class ModelMutationOptions(MutationOptions):
    lookup_field = "pk"
    model_operations = ["create", "update"]
    serializer_class = None
    permission_classes = []
    exclude = None
    return_field_name = "instance"
    return_field_type = None
