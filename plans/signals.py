import logging
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from records.utils import get_current_user, create_record
from .models import Plan

business_logger = logging.getLogger('business')


def _log_and_record(user, model, action, detail, instance_id):
    if action == 'create':
        business_logger.info(f"[{model}] CREATE: {detail} (user={user}, id={instance_id})")
    elif action == 'update':
        business_logger.info(f"[{model}] UPDATE: {detail} (user={user}, id={instance_id})")
    elif action == 'delete':
        business_logger.info(f"[{model}] DELETE: {detail} (user={user}, id={instance_id})")
    create_record(user, action, model, detail, instance_id)


@receiver(post_save, sender=Plan)
def log_create_plan(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'Plan', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=Plan)
def log_edit_plan(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Plan.objects.get(pk=instance.pk)
        except Plan.DoesNotExist:
            return
        for field in Plan._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'Plan', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=Plan)
def log_delete_plan(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'Plan', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)