import logging
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from records.utils import get_current_user, create_record
from .models import Requirement, Requirement_Delivered, RateRequirement

business_logger = logging.getLogger('business')


def _log_and_record(user, model, action, detail, instance_id):
    if action == 'create':
        business_logger.info(f"[{model}] CREATE: {detail} (user={user}, id={instance_id})")
    elif action == 'update':
        business_logger.info(f"[{model}] UPDATE: {detail} (user={user}, id={instance_id})")
    elif action == 'delete':
        business_logger.info(f"[{model}] DELETE: {detail} (user={user}, id={instance_id})")
    create_record(user, action, model, detail, instance_id)


@receiver(post_save, sender=Requirement)
def log_create_requirement(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'Requirement', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=Requirement)
def log_edit_requirement(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Requirement.objects.get(pk=instance.pk)
        except Requirement.DoesNotExist:
            return
        for field in Requirement._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'Requirement', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=Requirement)
def log_delete_requirement(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'Requirement', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)


@receiver(post_save, sender=Requirement_Delivered)
def log_create_requirement_delivered(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'Requirement_Delivered', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=Requirement_Delivered)
def log_edit_requirement_delivered(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Requirement_Delivered.objects.get(pk=instance.pk)
        except Requirement_Delivered.DoesNotExist:
            return
        for field in Requirement_Delivered._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'Requirement_Delivered', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=Requirement_Delivered)
def log_delete_requirement_delivered(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'Requirement_Delivered', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)


@receiver(post_save, sender=RateRequirement)
def log_create_rate_requirement(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'RateRequirement', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=RateRequirement)
def log_edit_rate_requirement(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = RateRequirement.objects.get(pk=instance.pk)
        except RateRequirement.DoesNotExist:
            return
        for field in RateRequirement._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'RateRequirement', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=RateRequirement)
def log_delete_rate_requirement(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'RateRequirement', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)