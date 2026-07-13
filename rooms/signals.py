import logging
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from records.utils import get_current_user, create_record
from .models import Property, Room, Sub_Room

business_logger = logging.getLogger('business')


def _log_and_record(user, model, action, detail, instance_id):
    if action == 'create':
        business_logger.info(f"[{model}] CREATE: {detail} (user={user}, id={instance_id})")
    elif action == 'update':
        business_logger.info(f"[{model}] UPDATE: {detail} (user={user}, id={instance_id})")
    elif action == 'delete':
        business_logger.info(f"[{model}] DELETE: {detail} (user={user}, id={instance_id})")
    create_record(user, action, model, detail, instance_id)


@receiver(post_save, sender=Room)
def log_create_room(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'Room', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=Room)
def log_edit_room(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Room.objects.get(pk=instance.pk)
        except Room.DoesNotExist:
            return
        for field in Room._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'Room', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=Room)
def log_delete_room(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'Room', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)


@receiver(post_save, sender=Property)
def log_create_property(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'Property', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=Property)
def log_edit_property(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Property.objects.get(pk=instance.pk)
        except Property.DoesNotExist:
            return
        for field in Property._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'Property', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=Property)
def log_delete_property(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'Property', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)


@receiver(post_save, sender=Sub_Room)
def log_create_sub_room(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'Sub_Room', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=Sub_Room)
def log_edit_sub_room(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Sub_Room.objects.get(pk=instance.pk)
        except Sub_Room.DoesNotExist:
            return
        for field in Sub_Room._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'Sub_Room', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=Sub_Room)
def log_delete_sub_room(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'Sub_Room', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)