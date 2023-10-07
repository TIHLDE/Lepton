import pytest

from rest_framework import status

from app.util.test_utils import get_api_client
from app.content.enums import ContentType


API_COMMENTS_BASE_URL = "/comments/"

def get_comments_url_detail(comment=None):
    return f"{API_COMMENTS_BASE_URL}{comment.id}/"

def get_comment_data(
    content_type,
    content_id,
    user=None,
    parent=None,
    allow_comments=True
):
    return {
        "body": "test comment body text",
        "author": user.user_id if user else None,
        "parent": parent.id if parent else None,
        "content_type": content_type,
        "content_id": content_id,
        "allow_comments": allow_comments
    }

def get_update_comment_data(comment, body):
    return {
        "id": comment.id,
        "body": body
    }


@pytest.mark.django_db
def test_retrieve_comment_as_user(user):
    pass


@pytest.mark.django_db
def test_create_comment_on_event_as_member(member, event):
    """
        An user of TIHLDE should be able to create a comment on an event. 
    """

    client = get_api_client(user=member)
    data = get_comment_data(ContentType.EVENT, event.id, user=member)

    response = client.post(API_COMMENTS_BASE_URL, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_child_comment_on_event_as_member(member, event, event_comment):
    """
        An user of TIHLDE should be able to create a child comment on an event.
    """

    client = get_api_client(user=member)
    data = get_comment_data(
        ContentType.EVENT,
        event.id, 
        user=member,
        parent=event_comment
    )

    response = client.post(API_COMMENTS_BASE_URL, data)
    data = response.data

    assert response.status_code == status.HTTP_201_CREATED
    assert data["parent"] == event_comment.id
    assert data["indent_level"] == 1


@pytest.mark.django_db
def test_create_oversized_thread_on_event_as_member(member, event, event_comment):
    """
        An user of TIHLDE should not be able to create a child comment 
        on an event which have achieved maximum thread length.
    """

    event_comment.indent_level = 3

    event_comment.save()

    client = get_api_client(user=member)
    data = get_comment_data(
        ContentType.EVENT,
        event.id,
        user=member,
        parent=event_comment
    )

    response = client.post(API_COMMENTS_BASE_URL, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_comment_on_news_as_member(member, news):
    """
        An user of TIHLDE should be able to create a comment on news. 
    """

    client = get_api_client(user=member)
    data = get_comment_data(ContentType.NEWS, news.id, user=member)

    response = client.post(API_COMMENTS_BASE_URL, data)
    
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_create_comment_on_event_as_anonymous_user(default_client, event):
    """
        An anonymous user should not be able to create a comment on an event.
    """

    data = get_comment_data(ContentType.EVENT, event.id)
    response = default_client.post(API_COMMENTS_BASE_URL, data=data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_create_comment_on_news_as_anonymous_user(default_client, news):
    """
        An anonymous user should not be able to create a comment on news.
    """

    data = get_comment_data(ContentType.EVENT, news.id)
    response = default_client.post(API_COMMENTS_BASE_URL, data=data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_create_comment_on_event_when_comments_not_allowed(member, event):
    """
        A member should not be able to create a comment on an event
        which does not allow comments.
    """

    client = get_api_client(user=member)
    data = get_comment_data(ContentType.EVENT, event.id, user=member, allow_comments=False)

    response = client.post(API_COMMENTS_BASE_URL, data)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_comment_on_news_when_comments_not_allowed(member, news):
    """
        A member should not be able to create a comment on news
        which does not allow comments.
    """

    client = get_api_client(user=member)
    data = get_comment_data(ContentType.EVENT, news.id, user=member, allow_comments=False)

    response = client.post(API_COMMENTS_BASE_URL, data)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_event_comment_as_member(member, event_comment):
    """
        A member should be able to update an event comment.
    """

    client = get_api_client(user=member)
    data = get_update_comment_data(event_comment, "Test update")
    url = get_comments_url_detail(event_comment)

    response = client.put(url, data)
    event_comment.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert event_comment.body == "Test update"


@pytest.mark.django_db
def test_update_news_comment_as_member(member, news_comment):
    """
        A member should be able to update a news comment.
    """

    client = get_api_client(user=member)
    data = get_update_comment_data(news_comment, "Test update")
    url = get_comments_url_detail(news_comment)

    response = client.put(url, data)
    news_comment.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert news_comment.body == "Test update"


@pytest.mark.django_db
def test_update_event_comment_as_anonymous_user(default_client, event_comment):
    """
        An anonymous user should not be able to update an event comment.
    """

    data = get_update_comment_data(event_comment, "Test update")
    url = get_comments_url_detail(event_comment)

    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_news_comment_as_anonymous_user(default_client, news_comment):
    """
        An anonymous user should not be able to update a news comment.
    """

    data = get_update_comment_data(news_comment, "Test update")
    url = get_comments_url_detail(news_comment)

    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    