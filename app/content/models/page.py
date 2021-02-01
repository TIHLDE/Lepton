import uuid

from django.db import models
from django.utils.text import slugify

from mptt.models import MPTTModel, TreeForeignKey

from app.util.models import BaseModel, OptionalImage


class Page(MPTTModel, OptionalImage, BaseModel):
    parent = TreeForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )
    page_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50, unique=False)
    slug = models.SlugField(max_length=50, unique=False)
    content = models.TextField(blank=True)

    class Meta:
        unique_together = ("parent", "slug")
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        ordering = ["title"]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @staticmethod
    def get_by_path(path):
        node = Page.objects.get(parent=None)
        if path == "":
            return node
        page_list = path.split("/")
        if page_list[-1] == "":
            page_list.remove("")
        for page in page_list:
            node = next(child for child in node.get_children() if child.slug == page)
        if node.slug != page_list[-1]:
            raise Page.DoesNotExist
        return node

    def get_path(self):
        family = self.get_ancestors(include_self=True)[1:]
        path = ""
        for member in family:
            path += f"{member.slug}/"
        return path

    def __str__(self):
        return f"{self.page_id} {self.title}"
