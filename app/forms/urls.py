from rest_framework import routers

from app.forms.views.form import FormViewSet
from app.forms.views.submission import SubmissionViewSet

router = routers.DefaultRouter()


router.register(r"/", FormViewSet, )
router.register(
    r"/(?P<form_id>[0-9a-f-]+)/submissions", SubmissionViewSet
)
