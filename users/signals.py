import logging
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from records.utils import get_current_user, create_record

User = get_user_model()
business_logger = logging.getLogger('business')


@receiver(post_save, sender=User)
def log_create_user(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        create_record(user, 'create', 'User', f'El usuario: {user} creó el registro {instance}', instance.id)
    business_logger.info(f"[USER] CREATE: {instance} creado (user={user}, id={instance.id})")


@receiver(pre_save, sender=User)
def log_edit_user(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = User.objects.get(pk=instance.pk)
        except User.DoesNotExist:
            return
        for field in User._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                create_record(user, 'update', 'User',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)
            business_logger.info(f"[USER] UPDATE: Campo '{field.name}' de '{old_value}' a '{new_value}' en {instance} (user={user})")


@receiver(post_delete, sender=User)
def log_delete_user(sender, instance, **kwargs):
    user = get_current_user()
    create_record(user, 'delete', 'User', f'El usuario: {user} eliminó el registro {instance}', instance.id)
    business_logger.info(f"[USER] DELETE: {instance} eliminado (user={user}, id={instance.id})")
