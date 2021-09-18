import graphene

import app.content.schema


class Query(
    app.content.schema.Query, graphene.ObjectType,
):
    pass


class Mutation(
    app.content.schema.Mutation, graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
