from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

class UserTest(APITestCase):
   def test_user_not_found(self):
      factory = APIRequestFactory()
      user = User.objects.get(user_id='zuimran')
      view = AccountDetail.as_view()

      request = factory.get('/user/zuimran')
      force_authenticate(request, user=user)
      response = view(request)
