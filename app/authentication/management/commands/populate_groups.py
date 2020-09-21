from django.core.management.base import BaseCommand

from app.authentication.models import Group

groups = [
    ("Hovedstyret", "HS"),
    ("Drift", "Drift"),
    ("Promo", "Promo"),
    ("Næringsliv og Kurs", "NoK"),
    ("Sosialen", "Sos"),
    ("NetKom", "NetKom"),
    ("JubKom", "JubKom"),
    ("TurKom", "TurKom"),
    ("KosKom", "KosKom"),
    ("ArrKom", "ArrKom"),
    ("FestKom", "FestKom"),
    ("ÅreKom", "ÅreKom"),
]


class Command(BaseCommand):
    args = ""
    help = "No help needed"

    def create_groups(self):
        for group in groups:
            newGroup = Group(name=group[0], abbr=group[1])
            newGroup.save()

    def handle(self, *args, **options):
        self.create_groups()
