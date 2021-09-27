import graphene


class ObjectField(graphene.Scalar):
    """Serialize error message from serializer."""

    @staticmethod
    def serialize(dt):
        return dt


class Output:
    message = ObjectField()
