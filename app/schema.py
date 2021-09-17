import graphene

import app.content.schema


class Query(
    app.content.schema.Query, graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query)
