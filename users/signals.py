from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Record
from threadlocals.threadlocals import get_thread_variable
@receiver(post_save, sender=User)
def log_user_activity(sender, instance, created, **kwargs):
    model="User"
    user = get_thread_variable('thread_user')
    if created:
        detail=f"El usuario {user} creo un  {instance}"
        action="create"
    else:
        detail=f"El usuario {user} desactivo al  {instance}"
        action="update"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=detail
    )