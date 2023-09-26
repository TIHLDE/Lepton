import pytest

from app.util.test_utils import get_api_client


API_COMMENTS_BASE_URL = "/comments/"

def get_comments_url_detail(comment=None):
    return f"{API_COMMENTS_BASE_URL}{comment.id}/"

def get_comment_data(content_type, content_id, user=None, parent=None):
    return {
        "body": "test comment body text",
        "author": user.user_id,
        "parent": None,
        "content_type": content_type,
        "content_id": content_id
    }


@pytest.mark.django_db
def test_retrieve_comment_as_user(user):
    pass


@pytest.mark.django_db
def test_create_comment_as_user(user, event):
    client = get_api_client(user=user)
    data = get_comment_data("event", event.id, user=user)

    response = client.post(API_COMMENTS_BASE_URL, data)