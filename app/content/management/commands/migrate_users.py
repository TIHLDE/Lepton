from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from app.common.enums import GroupType
from app.content.models import User
from app.content.models.user import CLASS
from app.group.models import Group, Membership

STUDY_FULL = (
    (1, "Dataingeniør"),
    (2, "Digital forretningsutvikling"),
    (3, "Digital infrastruktur og cybersikkerhet"),
    (4, "Digital samhandling"),
    (5, "Drift"),
    (6, "Informasjonsbehandling"),
)


class Command(BaseCommand):
    args = ""
    help = "Migrate users to class and study groups"

    def handle(self, *args, **options):
        self.migrate_year()
        self.migrate_study()

    @atomic
    def migrate_year(self):
        this_year = 2022

        for year, _ in CLASS:

            users = User.objects.filter(user_class=year)
            if year == -1:
                group_name = "Alumni"
            else:
                group_name = str(this_year - year)

            designated_group, _ = Group.objects.get_or_create(
                name=group_name, type=GroupType.STUDYYEAR
            )
            memberships = [
                Membership(user=user, group=designated_group) for user in users
            ]
            memberships = Membership.objects.bulk_create(memberships)
            self.style.SUCCESS(
                f"Successfully migrated {users.count()} users to {group_name} ({len(memberships)} new memberships)"
            )

    def migrate_study(self):
        for number, group_name in STUDY_FULL:
            users = User.objects.filter(user_study=number)
            designated_group, _ = Group.objects.get_or_create(
                name=group_name, type=GroupType.STUDY
            )
            memberships = [
                Membership(user=user, group=designated_group) for user in users
            ]
            memberships = Membership.objects.bulk_create(memberships)
            self.style.SUCCESS(
                f"Successfully migrated {users.count()} users to {group_name} ({len(memberships)} new memberships)"
            )
