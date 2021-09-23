import graphene

from app.forms.models import Form
from app.forms.types import FormUnionType


class FormQuery:
    forms = graphene.List(FormUnionType)

    @classmethod
    def resolve_forms(cls, root, info, *args, **kwargs):

        form_objects_all = Form.objects.all()
        print(form_objects_all)
        return form_objects_all
