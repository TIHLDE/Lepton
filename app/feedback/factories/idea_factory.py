from app.feedback.factories.feedback_factory import FeedbackFactory
from app.feedback.models.idea import Idea


class IdeaFactory(FeedbackFactory):
    class Meta:
        model = Idea
