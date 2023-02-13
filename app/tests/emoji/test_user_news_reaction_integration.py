from app.emoji.factories.user_news_reaction_factory import UserNewsReactionFactory
import pytest 
from app.common.enums import Groups
from app.emoji.serializers.user_news_reaction import UserNewsReactionSerializer
from app.util.test_utils import get_api_client
from app.emoji.models.user_news_reaction import UserNewsReaction
from app.content.factories.user_factory import UserFactory
from rest_framework import status


#Tester
#1. At en member kan lage en reaksjon
#2. At en ikke-member ikke kan lage en reaksjon
#3. At en member kan endre reaksjonen sin
#4. At en reaksjon kan fjernes
#5. At en member kun kan ha én reaksjon per nyhet
#6. At alle kan se reaksjoner på en nyhet
#7. At en member ikke kan reagere på vegne av en annen member
#8.At en member ikke kan reagere flere ganger på samme nyhet

#Til mandag 5.2.23 -> Få til put i postman -> insepct eleement på dev.tihlde.org og oppdater noe

#NB: per nå kan brukere reagere så mange ganger som de vil (har ikke composite pk på reactions)

# evt.
# At admin og HS kan lage egne custom emojies med navn ?? 
# At admin kan lage nye emojis til reaksjoner
# At admin kan bestemme hvilke emojis som kan brukes til å reagere på en nyhet
API_EMOJI_BASE_URL = "/emojis/"

def _get_reactions_url():
    return f"{API_EMOJI_BASE_URL}reactions/"

def _get_reactions_post_data(user, news, emoji):
    return {
        "user": user.user_id,
        "news": news.id,
        "emoji": emoji.id
    }
    
@pytest.mark.django_db
def test_that_a_member_can_react_on_news(member, news, emoji):
    """A member should be able to do leave a reaction on a news page"""

    url = _get_reactions_url()
    client = get_api_client(user=member)
    data = _get_reactions_post_data(member, news, emoji)

    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED

'''@pytest.mark.django_db
def test_that_a_non_member_cannot_react_on_news(default_client):
    """A non-member should not be able to leave a reaction on a news page"""
    url = _get_reactions_url()
    data = _get_reactions_post_data(default_client)
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_that_a_member_can_change_reaction(member):
    """A member should be able to change their reaction on a news page"""

    url = _get_reactions_url()
    client = get_api_client(user=member)
    data = _get_reactions_put_data(UserNewsReactionFactory())
    response = client.put(url, data)

    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_that_a_member_can_not_post_a_reaction_for_another_member(member):
    """A member should not be able to post a reaction for another member on a news page"""

    url = _get_reactions_url()
    client = get_api_client(user=member)

    reaction = UserNewsReactionFactory()
    #to do- bruk noe annet enn factory for å unngå dobbelt posting
    data = _get_reactions_post_data(user=member)
    response = client.put(url, data)

    assert member != reaction.user
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED #Skal sikkert være 403 forbidden

@pytest.mark.django_db
def test_that_a_member_can_not_post_multiple_reactions_on_the_same_news(member):
    """A member should not be able to post multiple reactions on the same news page"""

    url = _get_reactions_url()
    client = get_api_client(user=member)
    data = _get_reactions_post_data()
    response = client.post(url, data)
    response_2 = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response_2.status_code == status.HTTP_409_CONFLICT

@pytest.mark.django_db
def test_that_a_member_can_delete_their_reaction(request):
    """A member should be able to remove their reaction from a news page"""

    url = _get_reactions_url()
    client = get_api_client(user=request.user)
    data = _get_reactions_put_data()
    response = client.delete(url, data)

    assert response.status_code == status.HTTP_200_OK'''