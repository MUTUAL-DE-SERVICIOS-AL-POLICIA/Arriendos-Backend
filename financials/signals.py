import logging
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from records.utils import get_current_user, create_record
from .models import Payment, Warranty_Movement

business_logger = logging.getLogger('business')


def _log_and_record(user, model, action, detail, instance_id):
    if action == 'create':
        business_logger.info(f"[{model}] CREATE: {detail} (user={user}, id={instance_id})")
    elif action == 'update':
        business_logger.info(f"[{model}] UPDATE: {detail} (user={user}, id={instance_id})")
    elif action == 'delete':
        business_logger.info(f"[{model}] DELETE: {detail} (user={user}, id={instance_id})")
    create_record(user, action, model, detail, instance_id)


@receiver(post_save, sender=Payment)
def log_create_payment(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'Payment', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=Payment)
def log_edit_payment(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Payment.objects.get(pk=instance.pk)
        except Payment.DoesNotExist:
            return
        for field in Payment._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'Payment', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=Payment)
def log_delete_payment(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'Payment', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)


@receiver(post_save, sender=Warranty_Movement)
def log_create_warranty_movement(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'Warranty_Movement', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=Warranty_Movement)
def log_edit_warranty_movement(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Warranty_Movement.objects.get(pk=instance.pk)
        except Warranty_Movement.DoesNotExist:
            return
        for field in Warranty_Movement._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'Warranty_Movement', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=Warranty_Movement)
def log_delete_warranty_movement(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'Warranty_Movement', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)