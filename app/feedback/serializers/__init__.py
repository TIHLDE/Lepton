from app.feedback.serializers.bug import (
    BugDetailSerializer,
    BugCreateSerializer,
    BugUpdateSerializer,
)
from app.feedback.serializers.idea import (
    IdeaDetailSerializer,
    IdeaCreateSerializer,
    IdeaUpdateSerializer,
)
from app.feedback.serializers.feedback import FeedbackListPolymorphicSerializer
from app.feedback.serializers.assginee import (
    AssigneeSerializer,
    AssigneeCreateUpdateDeleteSerializer,
)
