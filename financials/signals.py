import logging
from django.db.models.signals import post_save, pre_save, post_delete
from threadlocals.threadlocals import get_thread_variable
from django.dispatch import receiver
from users.models import Record
from .models import *

business_logger = logging.getLogger('business')

@receiver(post_save, sender=Payment)
def log_create_payment(sender, instance, created, **kwargs):
    model="Payment"
    user = get_thread_variable('thread_user')
    if created:
        detail=f"El usuario: {user} creó el registro {instance}"
        action="create"
        try:
            Record.objects.create(user=user, action=action, model=model, detail=detail, instance_id=instance.id)
        except Exception as e:
            business_logger.error(f"[PAYMENT] Audit record failed: {e}")
        business_logger.info(f"[PAYMENT] CREATE: {instance} creado (user={user}, id={instance.id})")

@receiver(pre_save, sender=Payment)
def log_edit_payment(sender, instance, **kwargs):
    action="update"
    model="Payment"
    if instance.pk is not None:
        old_instance = Payment.objects.get(pk=instance.pk)
        for field in Payment._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            user = get_thread_variable('thread_user')
            if old_value != new_value:
                try:
                    Record.objects.create(user=user, action=action, model=model, detail=f'El usuario: {user} realizó un cambió en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}', instance_id=instance.id)
                except Exception as e:
                    business_logger.error(f"[PAYMENT] Audit record failed: {e}")
                business_logger.info(f"[PAYMENT] UPDATE: Campo '{field.name}' de '{old_value}' a '{new_value}' en {instance} (user={user})")

@receiver(post_delete, sender=Payment)
def log_delete_payment(sender, instance, **kwargs):
    model="Payment"
    user = get_thread_variable('thread_user')
    action="delete"
    try:
        Record.objects.create(user=user, action=action, model=model, detail=f"El usuario: {user} eliminó el registro {instance}", instance_id=instance.id)
    except Exception as e:
        business_logger.error(f"[PAYMENT] Audit record failed: {e}")
    business_logger.info(f"[PAYMENT] DELETE: {instance} eliminado (user={user}, id={instance.id})")

@receiver(post_save, sender=Warranty_Movement)
def log_create_warranty_movement(sender, instance, created, **kwargs):
    model="Warranty_Movement"
    user = get_thread_variable('thread_user')
    if created:
        detail=f"El usuario: {user} creó el registro {instance}"
        action="create"
        try:
            Record.objects.create(user=user, action=action, model=model, detail=detail, instance_id=instance.id)
        except Exception as e:
            business_logger.error(f"[WARRANTY_MOVEMENT] Audit record failed: {e}")
        business_logger.info(f"[WARRANTY_MOVEMENT] CREATE: {instance} creado (user={user}, id={instance.id})")

@receiver(pre_save, sender=Warranty_Movement)
def log_edit_warranty_movement(sender, instance, **kwargs):
    action="update"
    model="Warranty_Movement"
    if instance.pk is not None:
        old_instance = Warranty_Movement.objects.get(pk=instance.pk)
        for field in Warranty_Movement._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            user = get_thread_variable('thread_user')
            if old_value != new_value:
                try:
                    Record.objects.create(user=user, action=action, model=model, detail=f'El usuario: {user} realizó un cambió en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}', instance_id=instance.id)
                except Exception as e:
                    business_logger.error(f"[WARRANTY_MOVEMENT] Audit record failed: {e}")
                business_logger.info(f"[WARRANTY_MOVEMENT] UPDATE: Campo '{field.name}' de '{old_value}' a '{new_value}' en {instance} (user={user})")

@receiver(post_delete, sender=Warranty_Movement)
def log_delete_warranty_movement(sender, instance, **kwargs):
    model="Warranty_Movement"
    user = get_thread_variable('thread_user')
    action="delete"
    try:
        Record.objects.create(user=user, action=action, model=model, detail=f"El usuario: {user} eliminó el registro {instance}", instance_id=instance.id)
    except Exception as e:
        business_logger.error(f"[WARRANTY_MOVEMENT] Audit record failed: {e}")
    business_logger.info(f"[WARRANTY_MOVEMENT] DELETE: {instance} eliminado (user={user}, id={instance.id})")
