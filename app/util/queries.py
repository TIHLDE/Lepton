class BaseQuery:
    view = None

    @classmethod
    def __create_view(cls, info, action_map, **kwargs):
        view = cls.view()
        view.kwargs = kwargs
        view.action_map = action_map
        view.request = view.initialize_request(info.context, *(), **kwargs)
        view.check_permissions(view.request)
        return view

    @classmethod
    def resolve_retrieve(cls, info, **kwargs):
        view = cls.__create_view(info, action_map={"get": "retrieve"}, **kwargs)
        return view.get_object()

    @classmethod
    def resolve_list(cls, info, **kwargs):
        view = cls.__create_view(info, action_map={"get": "list"}, **kwargs)
        return view.get_queryset()
