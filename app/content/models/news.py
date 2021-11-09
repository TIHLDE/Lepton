from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.util.models import Content, TimeStampedModel


class News(TimeStampedModel, Content, BasePermissionModel):
    write_access = AdminGroup.all()

    class Meta:
        verbose_name_plural = "News"

    def __str__(self):
        return f"{self.title} - {self.header} ({len(self.body)} characters)"

    @property
    def website_url(self):
        return f"/nyheter/{self.id}/"
