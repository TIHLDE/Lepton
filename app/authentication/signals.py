from app.content.models.user import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from app.authentication.auth0 import get_user_study_programs
from app.common.enums import Groups
from app.group.models.group import Group
from app.group.models.membership import Membership

@receiver(post_save, sender=User)
def set_user_groups(sender, instance: User, created, **kwargs):
    # Only run this when the user if first created.
    if not created:
        return

    study_programs = get_user_study_programs(instance.user_id) # Return example: [('BIDATA', 2020), ...]

    # For every program reported by Feide, try to add user groups.
    for program in study_programs:
        program_slug = _get_program_group_slug(program)
        program_year = _get_program_year(program)

        # Do not add any groups if program is not part of TIHLDE.
        if not program_slug:
            continue

        # Automatically activate account when program is verified.
        TIHLDE = Group.objects.get(slug=Groups.TIHLDE)
        Membership.objects.get_or_create(user=instance, group=TIHLDE)
            
        program_group = Group.objects.get(slug=program_slug)
        Membership.objects.get_or_create(user=instance, group = program_group)

        year_group = Group.objects.get(slug=program_year)
        Membership.objects.get_or_create(user=instance, group = year_group)


def _get_program_group_slug(program):
    program_codes = ["BIDATA", "ITBAITBEDR", "BDIGSEC", "ITMAIKTSA", "ITBAINFODR", "ITBAINFO"]
    program_slugs = ["dataingenir", "digital-forretningsutvikling", "digital-infrastruktur-og-cybersikkerhet", "digital-samhandling", "drift-studie", "informasjonsbehandling"]

    try:
        index = program_codes.index(program[0])
    except:
        return None
    
    return program_slugs[index]

def _get_program_year(program):
    return program[1]
