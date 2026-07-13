import logging
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from records.utils import get_current_user, create_record
from .models import State, Rental, Event_Type, Selected_Product, Additional_Hour_Applied

business_logger = logging.getLogger('business')


def _log_and_record(user, model, action, detail, instance_id):
    if action == 'create':
        business_logger.info(f"[{model}] CREATE: {detail} (user={user}, id={instance_id})")
    elif action == 'update':
        business_logger.info(f"[{model}] UPDATE: {detail} (user={user}, id={instance_id})")
    elif action == 'delete':
        business_logger.info(f"[{model}] DELETE: {detail} (user={user}, id={instance_id})")
    create_record(user, action, model, detail, instance_id)


@receiver(post_save, sender=State)
def log_create_state(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'State', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=State)
def log_edit_state(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = State.objects.get(pk=instance.pk)
        except State.DoesNotExist:
            return
        for field in State._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'State', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=State)
def log_delete_state(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'State', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)


@receiver(post_save, sender=Rental)
def log_create_rental(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'Rental', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=Rental)
def log_edit_rental(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Rental.objects.get(pk=instance.pk)
        except Rental.DoesNotExist:
            return
        for field in Rental._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'Rental', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=Rental)
def log_delete_rental(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'Rental', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)


@receiver(post_save, sender=Event_Type)
def log_create_event_type(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'Event_Type', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=Event_Type)
def log_edit_event_type(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Event_Type.objects.get(pk=instance.pk)
        except Event_Type.DoesNotExist:
            return
        for field in Event_Type._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'Event_Type', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=Event_Type)
def log_delete_event_type(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'Event_Type', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)


@receiver(post_save, sender=Selected_Product)
def log_create_selected_product(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'Selected_Product', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=Selected_Product)
def log_edit_selected_product(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Selected_Product.objects.get(pk=instance.pk)
        except Selected_Product.DoesNotExist:
            return
        for field in Selected_Product._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'Selected_Product', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=Selected_Product)
def log_delete_selected_product(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'Selected_Product', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)


@receiver(post_save, sender=Additional_Hour_Applied)
def log_create_additional_hour_applied(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'Additional_Hour_Applied', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=Additional_Hour_Applied)
def log_edit_additional_hour_applied(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Additional_Hour_Applied.objects.get(pk=instance.pk)
        except Additional_Hour_Applied.DoesNotExist:
            return
        for field in Additional_Hour_Applied._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'Additional_Hour_Applied', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=Additional_Hour_Applied)
def log_delete_additional_hour_applied(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'Additional_Hour_Applied', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)