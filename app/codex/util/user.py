from app.codex.enums import CodexGroups


def user_is_leader_of_codex_group(user):
    return (
        user.is_leader_of(CodexGroups.DRIFT) or
        user.is_leader_of(CodexGroups.INDEX)
    )