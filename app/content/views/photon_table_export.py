import base64
import datetime
import decimal

from django.db import connection
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.common.permissions import is_admin_user, set_user_id

# The exact tables Photon's migration pipeline reads (its phases are all
# plain `SELECT *`). Nothing outside this list can be exported, and the
# table name is only ever interpolated from this list — never from input.
ALLOWED_TABLES = {
    "career_jobpost",
    "communication_notification",
    "content_category",
    "content_event",
    "content_event_favorite_users",
    "content_news",
    "content_prioritypool",
    "content_prioritypool_groups",
    "content_registration",
    "content_strike",
    "content_user",
    "django_content_type",
    "emoji_reaction",
    "forms_answer",
    "forms_answer_selected_options",
    "forms_eventform",
    "forms_field",
    "forms_form",
    "forms_groupform",
    "forms_option",
    "forms_submission",
    "group_fine",
    "group_group",
    "group_membership",
    "payment_order",
    "payment_paidevent",
}

# Columns that must not leave this database even for the migration.
# Photon sets its own placeholder password; users authenticate via Feide.
EXCLUDED_COLUMNS = {
    "content_user": {"password"},
}

MAX_LIMIT = 1000


def _primary_key_columns(table):
    """Primary key column names, for deterministic LIMIT/OFFSET paging."""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = %s
              AND CONSTRAINT_NAME = 'PRIMARY'
            ORDER BY ORDINAL_POSITION
            """,
            [table],
        )
        return [row[0] for row in cursor.fetchall()]


def _jsonable(value):
    """Coerce driver types into JSON, keeping timestamps ISO-8601."""
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, datetime.timedelta):
        return value.total_seconds()
    if isinstance(value, decimal.Decimal):
        return str(value)
    if isinstance(value, (bytes, bytearray)):
        return base64.b64encode(value).decode("ascii")
    return value


@api_view(["GET"])
def photon_table_export(request):
    """
    Read-only, paged bulk export of one migration table, for the one-time
    move to Photon (the new backend). Photon has no access to this database,
    so it consumes this endpoint instead of a direct SQL connection — the
    JSON rows stand in for the `SELECT *` its migration phases would run.

    Locked to superusers who are also in HS/Index, same as the user export,
    and like it this should be removed once the migration is done.

    Query params: table (required), offset, limit (max 1000).
    Header: X-Csrf-Token — the caller's auth token.
    """
    set_user_id(request)

    if request.user is None:
        return Response(
            {"detail": "Manglende autentiseringsinformasjon."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not (is_admin_user(request) and request.user.is_superuser):
        return Response(
            {"detail": "Krever superbruker i HS/Index."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # The name interpolated into SQL is the allowlist's own element, not the
    # request string — the request only selects which hardcoded name to use,
    # so no user-controlled value ever reaches the query.
    requested = request.query_params.get("table", "")
    table = next((name for name in ALLOWED_TABLES if name == requested), None)
    if table is None:
        return Response(
            {"detail": f"Ukjent tabell. Gyldige: {sorted(ALLOWED_TABLES)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        offset = max(int(request.query_params.get("offset", 0)), 0)
        limit = min(
            max(int(request.query_params.get("limit", MAX_LIMIT)), 1), MAX_LIMIT
        )
    except ValueError:
        return Response(
            {"detail": "offset og limit må være heltall."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    order_by = _primary_key_columns(table)
    order_sql = " ORDER BY " + ", ".join(f"`{c}`" for c in order_by) if order_by else ""

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM `{table}`")  # nosec — allowlisted
        (total,) = cursor.fetchone()

        cursor.execute(
            f"SELECT * FROM `{table}`{order_sql} LIMIT %s OFFSET %s",  # nosec
            [limit, offset],
        )
        excluded = EXCLUDED_COLUMNS.get(table, set())
        keep = [
            index
            for index, column in enumerate(cursor.description)
            if column[0] not in excluded
        ]
        columns = [cursor.description[index][0] for index in keep]
        rows = [[_jsonable(row[index]) for index in keep] for row in cursor.fetchall()]

    return Response(
        {
            "table": table,
            "count": total,
            "offset": offset,
            "limit": limit,
            "columns": columns,
            "rows": rows,
        }
    )
