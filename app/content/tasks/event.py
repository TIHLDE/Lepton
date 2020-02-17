from celery import shared_task
from ..models.user_event import UserEvent



@shared_task
def event_unregister_deadline_schedular(pk):
  user_mail_list = []
  [user_mail_list.append(user_event.user.email) for user_event in UserEvent.objects.filter(event__pk=pk)]
  print(user_mail_list)

@shared_task
def event_unregister_deadline_schedular(pk):
  user_mail_list = []
  [user_mail_list.append(user_event.user.email) for user_event in UserEvent.objects.filter(event__pk=pk)]
  print(user_mail_list)

@shared_task
def event_unregister_deadline_schedular(pk):
  user_mail_list = []
  [user_mail_list.append(user_event.user.email) for user_event in UserEvent.objects.filter(event__pk=pk)]
  print(user_mail_list)

