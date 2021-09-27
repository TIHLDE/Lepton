from graphene_django.types import ErrorType


class BaseMixin:
    class Meta:
        abstract = True


class ListModelMixin(BaseMixin):
    class Meta:
        abstract = True

    @classmethod
    def resolve_list(cls, root, info, **kwargs):
        cls.check_permissions(request=info)
        return cls.get_queryset()


class RetrieveModelMixin(BaseMixin):
    class Meta:
        abstract = True

    @classmethod
    def resolve_retrieve(cls, root, info, **kwargs):
        return cls.get_object(request=info, **kwargs)


class MutationMixin(BaseMixin):
    class Meta:
        abstract = True

    @classmethod
    def mutate(cls, root, info, **input):
        return cls.resolve_mutation(root, info, **input)


class SerializerMutationMixin(BaseMixin):
    class Meta:
        abstract = True

    @classmethod
    def resolve_mutation(cls, root, info, **kwargs):
        return cls.mutate_and_get_payload(root, info, **kwargs)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        serializer = cls.get_serializer(root, info, **input)

        if serializer.is_valid():
            instance = cls.perform_mutate(serializer, info)
            return cls.success_response(instance)
        else:
            errors = ErrorType.from_errors(serializer.errors)
            return errors

    @classmethod
    def perform_mutate(cls, serializer, info):
        cls.check_permissions(info)
        return serializer.save()

    @classmethod
    def success_response(cls, instance):
        """Return a success response."""
        return cls(**{cls._meta.return_field_name: instance, "errors": []})
