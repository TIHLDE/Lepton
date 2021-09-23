from graphene_django.types import ErrorType


class ListModelMixin:
    @classmethod
    def resolve_list(cls, root, info, **kwargs):
        cls.check_permissions(request=info)
        return cls.get_queryset()


class RetrieveModelMixin:
    @classmethod
    def resolve_retrieve(cls, root, info, **kwargs):
        return cls.get_object(request=info, **kwargs)


# TODO: handle update properly
class MutationMixin:
    @classmethod
    def mutate(cls, root, info, **input):
        return cls.resolve_mutation(root, info, **input)


class SerializerMutationMixin:
    @classmethod
    def resolve_mutation(cls, root, info, **kwargs):
        return cls.mutate_and_get_payload(root, info, **kwargs)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        serializer = cls.get_serializer(root, info, **input)

        if serializer.is_valid():
            return cls.perform_mutate(serializer, info)
        else:
            errors = ErrorType.from_errors(serializer.errors)
            return errors

    @classmethod
    def perform_mutate(cls, serializer, info):
        return serializer.save()
