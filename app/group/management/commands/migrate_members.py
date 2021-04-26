from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from app.common.enums import Groups
from app.content.models import User
from app.group.models import Group, Membership

GROUPS_TIHLDE_SLUG = str(Groups.TIHLDE).lower()


class Command(BaseCommand):
    args = ""
    help = "Migrate TIHLDE members to our TIHLDE Group"

    def handle(self, *args, **options):
        self.migrate_tihlde_members()

    @atomic
    def migrate_tihlde_members(self):
        users = User.objects.filter(is_TIHLDE_member=True)
        tihlde = Group.objects.get(slug=GROUPS_TIHLDE_SLUG)
        memberships = (Membership(user=user, group=tihlde) for user in users)
        Membership.objects.bulk_create(memberships)
        self.stdout.write(self.style.SUCCESS("Successfully migrated TIHLDE members!"))
