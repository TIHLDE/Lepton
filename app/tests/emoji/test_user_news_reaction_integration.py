from app.emoji.factories.user_news_reaction_factory import UserNewsReactionFactory
import pytest 
from app.common.enums import Groups
from app.emoji.serializers.user_news_reaction import UserNewsReactionSerializer
from app.util.test_utils import get_api_client
from rest_framework import status


#Tester
#1. At en member kan lage en reaksjon
#2. At en ikke-member ikke kan lage en reaksjon
#3. At en reaksjon kan endres
#4. At en reaksjon kan fjernes
#5. At en member kun kan ha én reaksjon per nyhet
#6. At alle kan se reaksjoner på en nyhet

# evt.
# At admin og HS kan lage egne custom emojies med navn ?? 
API_EMOJI_BASE_URL = "/emojies/"

def _get_user_badges_url():
    return f"/users/me{API_EMOJI_BASE_URL}"
    
@pytest.mark.django_db
def test_that_a_member_can_react_on_news(member):
    """A member should be able to do leave a reaction on a news page"""

    url = _get_user_badges_url()
    client = get_api_client(user=member)
    data = UserNewsReactionFactory()
    response = client.post(url, data)

    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_that_a_non_member_cannot_react_on_news(member):
    """A non-member should not be able to leave a reaction on a news page"""

    url = _get_user_badges_url()
    client = get_api_client(user=member)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
