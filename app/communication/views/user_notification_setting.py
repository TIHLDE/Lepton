from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.common.mixins import LoggingViewSetMixin
from app.common.permissions import BasicViewPermission
from app.communication.enums import UserNotificationSettingType
from app.communication.mixins import APIUserNotificationSettingErrorsMixin
from app.communication.models import UserNotificationSetting
from app.communication.serializers import UserNotificationSettingSerializer


class UserNotificationSettingViewSet(
    APIUserNotificationSettingErrorsMixin,
    LoggingViewSetMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):

    queryset = UserNotificationSetting.objects.all()
    serializer_class = UserNotificationSettingSerializer
    permission_classes = [BasicViewPermission]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        try:
            user_notification_setting = UserNotificationSetting.objects.get(
                user=user, notification_type=request.data["notification_type"]
            )
            for key, value in request.data.items():
                setattr(user_notification_setting, key, value)
            user_notification_setting.full_clean()
            user_notification_setting.save()
        except UserNotificationSetting.DoesNotExist:
            user_notification_setting = UserNotificationSetting(
                user=user, **request.data
            )
            user_notification_setting.full_clean()
            user_notification_setting.save()
        user_notification_setting_serializer = UserNotificationSettingSerializer(
            self.get_queryset(), many=True
        )
        return Response(
            user_notification_setting_serializer.data, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], url_path="choices")
    def choices(self, _request, *_args, **_kwargs):
        return Response(
            list(
                map(
                    lambda choice: {"notification_type": choice[0], "label": choice[1]},
                    UserNotificationSettingType.choices,
                )
            ),
            status=status.HTTP_200_OK,
        )
