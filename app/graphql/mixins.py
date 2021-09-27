class ListModelMixin:
    @classmethod
    def resolve_list(cls, root, info, **kwargs):
        cls.check_permissions(request=info)
        return cls.get_queryset()


class RetrieveModelMixin:
    @classmethod
    def resolve_retrieve(cls, root, info, **kwargs):
        return cls.get_object(request=info, **kwargs)


class MutationMixin:
    class Meta:
        abstract = True

    @classmethod
    def mutate(cls, root, info, **input):
        return cls.resolve_mutation(root, info, **input)


class SerializerMutationMixin:
    class Meta:
        abstract = True
