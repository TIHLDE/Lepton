from django.contrib.contenttypes.models import ContentType
from django.db import migrations


class UpdateContentType(migrations.RunPython):
    """
    Database migration operation to update a ContentType
    Necessary to run together with `AlterModelTable` to avoid breaking LogEntries.

    Ex.:
    ```
    migrations.AlterModelTable(
        name='Notification',
        table='communication_notification',
    ),
    UpdateContentType(app='content', model='notification', new_app='communication')
    ```

    Found at: https://stackoverflow.com/a/61837871
    """

    def _update_contenttype_func(
        self, old_app: str, old_model: str, new_app: str, new_model: str
    ):
        def func(_apps, _schema_editor):
            ContentType.objects.filter(app_label=old_app, model=old_model).update(
                app_label=new_app, model=new_model
            )
            ContentType.objects.clear_cache()

        return func

    def __init__(
        self, app: str, model: str, new_app: str = None, new_model: str = None
    ):
        if new_app is None:
            new_app = app
        if new_model is None:
            new_model = model
        self.app = app
        self.model = model
        self.new_app = new_app
        self.new_model = new_model
        super().__init__(
            code=self._update_contenttype_func(
                old_app=app, old_model=model, new_app=new_app, new_model=new_model
            ),
            reverse_code=self._update_contenttype_func(
                old_app=new_app, old_model=new_model, new_app=app, new_model=model
            ),
        )

    def describe(self):
        return (
            f"Update ContentType {self.app}.{self.model}"
            f" to {self.new_app}.{self.new_model}"
        )
