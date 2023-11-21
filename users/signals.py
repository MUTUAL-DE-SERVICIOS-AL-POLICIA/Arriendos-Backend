from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Record
from threadlocals.threadlocals import get_thread_variable
@receiver(post_save, sender=User)
def log_create_user(sender, instance, created, **kwargs):
    model="User"
    user = get_thread_variable('thread_user')
    if created:
        detail=f"El usuario: {user} creó el registro {instance}"
        action="create"
        Record.objects.create(
            user=user,
            action=action,
            model=model,
            detail=detail,
            instance_id =instance.id
        )
@receiver(pre_save, sender=User)
def log_edit_user(sender, instance, **kwargs):
    action="update"
    model="User"
    if instance.pk is not None:
        old_instance = User.objects.get(pk=instance.pk)
        for field in User._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            user = get_thread_variable('thread_user')
            if old_value != new_value:
                Record.objects.create(
                    user=instance,
                    action=action,
                    model=model,
                    detail=f'El usuario: {instance.username} inició sesión',
                    instance_id = instance.id
                )
          
@receiver(post_delete, sender=User)
def log_delete_user(sender, instance, **kwargs):
    model="User"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}",
        instance_id =instance.id
    )