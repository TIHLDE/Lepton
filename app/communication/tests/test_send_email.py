@pytest.mark.django_db
class TestSendEmailEndpoint:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.url = reverse("send_email")  # Make sure the URL name is correctly set in your `urls.py`
        self.api_key = API_KEY  # Correct API key
        self.user = UserFactory()  # Create a test user
        self.headers = {"HTTP_EMAIL_API_KEY": self.api_key}

    @patch("app.communication.notifier.Notify.send")
    def test_send_email_success(self, mock_notify_send):
        """
        Test case for successfully sending an email via the send-email/ endpoint.
        """
        data = {
            "user_id": self.user.id,
            "notification_type": "EVENT_INFO",  # Adjust this to match your enum values
            "title": "Test Notification",
            "paragraphs": ["Paragraph 1", "Paragraph 2"],
        }

        response = self.client.post(self.url, data, format="json", **self.headers)

        # Assert that the request was successful
        assert response.status_code == 200
        assert response.data["detail"] == "Notification sent successfully."

        # Ensure that the Notify.send() method was called
        mock_notify_send.assert_called_once()

    def test_invalid_api_key(self):
        """
        Test case for invalid API key resulting in a 403 Forbidden response.
        """
        data = {
            "user_id": self.user.id,
            "notification_type": "EVENT_INFO",
            "title": "Test Notification",
            "paragraphs": ["Paragraph 1", "Paragraph 2"],
        }

        # Use an incorrect API key
        headers = {"HTTP_EMAIL_API_KEY": "wrong_api_key"}

        response = self.client.post(self.url, data, format="json", **headers)

        # Assert that the response is Forbidden
        assert response.status_code == 403
        assert response.data["detail"] == "Invalid API key"

    def test_missing_required_fields(self):
        """
        Test case for missing required fields (e.g., user_id, paragraphs).
        """
        data = {
            "title": "Test Notification",
            "notification_type": "EVENT_INFO",
        }

        response = self.client.post(self.url, data, format="json", **self.headers)

        # Assert that the response is a Bad Request
        assert response.status_code == 400
        assert "user_id" in response.data["detail"]

    def test_user_not_found(self):
        """
        Test case for when a non-existent user ID is provided.
        """
        data = {
            "user_id": 9999,  # Non-existent user ID
            "notification_type": "EVENT_INFO",
            "title": "Test Notification",
            "paragraphs": ["Paragraph 1"]
        }

        response = self.client.post(self.url, data, format="json", **self.headers)

        # Assert that the response is Not Found
        assert response.status_code == 404
        assert response.data["detail"] == "User not found."

    @patch("app.communication.notifier.Notify.send")
    def test_email_created_in_db(self, mock_notify_send):
        """
        Test case to ensure that an email is created in the database for the user who has opted in.
        """
        # UserFactory is used to create test users, and you could use UserNotificationSettingFactory if settings need to be considered
        data = {
            "user_id": self.user.id,
            "notification_type": "EVENT_INFO",
            "title": "Test Notification",
            "paragraphs": ["Paragraph 1", "Paragraph 2"]
        }

        response = self.client.post(self.url, data, format="json", **self.headers)

        # Assert that the response was successful
        assert response.status_code == 200

        # Check if Mail was created in the database
        assert Mail.objects.count() == 1
        mock_notify_send.assert_called_once()
