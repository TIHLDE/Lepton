from django.core.management.base import BaseCommand

from app.content.models import Category

categories = [
    "Alkoholfritt",
    "Allmøte",
    "Bedriftpresentasjon",
    "Bedriftseksursjon",
    "Fest",
    "Generalforsamling",
    "Kurs",
    "Tur",
    "Annet",
]


class Command(BaseCommand):
    args = ""
    help = "No help needed"

    def create_categories(self):
        for c in categories:
            category = Category(text=c)
            category.save()

    def handle(self, *args, **options):
        self.create_categories()
