import pytest

from app.content.util.feide_utils import parse_feide_groups


@pytest.mark.django_db
def test_parse_feide_groups():
    """A list of group ids should return the slugs that is in TIHLDE"""
    groups = [
        "fc:fs:fs:prg:ntnu.no:BDIGSEC",
        "fc:fs:fs:prg:ntnu.no:ITBAITBEDR",
        "fc:fs:fs:prg:ntnu.no:ITJEETTE",
        "fc:fs:fs:prg:ntnu.no:ITJESE",
        "fc:fs:fs:prg:ntnu.no:BDIGSEREC",
        "fc:fs:fs:prg:ntnu.no:BIDATA",
        "fc:fs:fs:prg:ntnu.no:ITMAIKTSA",
        "fc:fs:fs:prg:ntnu.no:ITBAINFODR",
        "fc:fs:fs:prg:ntnu.no:ITBAINFO",
    ]

    slugs = parse_feide_groups(groups)

    correct_slugs = [
        "dataingenir",
        "digital-forretningsutvikling",
        "digital-infrastruktur-og-cybersikkerhet",
        "digital-samhandling",
        "drift-studie",
        "informasjonsbehandling",
    ]

    assert sorted(slugs) == sorted(correct_slugs)
