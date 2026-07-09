import logging
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
User = get_user_model()
from users.models import Record
from threadlocals.threadlocals import get_thread_variable

business_logger = logging.getLogger('business')

@receiver(post_save, sender=User)
def log_create_user(sender, instance, created, **kwargs):
    model="User"
    user = get_thread_variable('thread_user')
    if created:
        detail=f"El usuario: {user} creó el registro {instance}"
        action="create"
        try:
            Record.objects.create(user=user, action=action, model=model, detail=detail, instance_id=instance.id)
        except Exception as e:
            business_logger.error(f"[USER] Audit record failed: {e}")
        business_logger.info(f"[USER] CREATE: {instance} creado (user={user}, id={instance.id})")

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
                try:
                    Record.objects.create(user=user, action=action, model=model, detail=f'El usuario: {user} realizó un cambió en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}', instance_id=instance.id)
                except Exception as e:
                    business_logger.error(f"[USER] Audit record failed: {e}")
                business_logger.info(f"[USER] UPDATE: Campo '{field.name}' de '{old_value}' a '{new_value}' en {instance} (user={user})")

@receiver(post_delete, sender=User)
def log_delete_user(sender, instance, **kwargs):
    model="User"
    user = get_thread_variable('thread_user')
    action="delete"
    try:
        Record.objects.create(user=user, action=action, model=model, detail=f"El usuario: {user} eliminó el registro {instance}", instance_id=instance.id)
    except Exception as e:
        business_logger.error(f"[USER] Audit record failed: {e}")
    business_logger.info(f"[USER] DELETE: {instance} eliminado (user={user}, id={instance.id})")
