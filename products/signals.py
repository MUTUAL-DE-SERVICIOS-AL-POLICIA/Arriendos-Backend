import logging
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from records.utils import get_current_user, create_record
from .models import Rate, HourRange, Product, Price, Price_Additional_Hour

business_logger = logging.getLogger('business')


def _log_and_record(user, model, action, detail, instance_id):
    if action == 'create':
        business_logger.info(f"[{model}] CREATE: {detail} (user={user}, id={instance_id})")
    elif action == 'update':
        business_logger.info(f"[{model}] UPDATE: {detail} (user={user}, id={instance_id})")
    elif action == 'delete':
        business_logger.info(f"[{model}] DELETE: {detail} (user={user}, id={instance_id})")
    create_record(user, action, model, detail, instance_id)


@receiver(post_save, sender=Rate)
def log_create_rate(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'Rate', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=Rate)
def log_edit_rate(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Rate.objects.get(pk=instance.pk)
        except Rate.DoesNotExist:
            return
        for field in Rate._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'Rate', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=Rate)
def log_delete_rate(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'Rate', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)


@receiver(post_save, sender=HourRange)
def log_create_hour_range(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'HourRange', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=HourRange)
def log_edit_hour_range(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = HourRange.objects.get(pk=instance.pk)
        except HourRange.DoesNotExist:
            return
        for field in HourRange._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'HourRange', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=HourRange)
def log_delete_hour_range(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'HourRange', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)


@receiver(post_save, sender=Product)
def log_create_product(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'Product', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=Product)
def log_edit_product(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Product.objects.get(pk=instance.pk)
        except Product.DoesNotExist:
            return
        for field in Product._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'Product', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=Product)
def log_delete_product(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'Product', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)


@receiver(post_save, sender=Price)
def log_create_price(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'Price', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=Price)
def log_edit_price(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Price.objects.get(pk=instance.pk)
        except Price.DoesNotExist:
            return
        for field in Price._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'Price', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=Price)
def log_delete_price(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'Price', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)


@receiver(post_save, sender=Price_Additional_Hour)
def log_create_price_additional_hour(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        _log_and_record(user, 'Price_Additional_Hour', 'create', f'El usuario: {user} creó el registro {instance}', instance.id)


@receiver(pre_save, sender=Price_Additional_Hour)
def log_edit_price_additional_hour(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Price_Additional_Hour.objects.get(pk=instance.pk)
        except Price_Additional_Hour.DoesNotExist:
            return
        for field in Price_Additional_Hour._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                _log_and_record(user, 'Price_Additional_Hour', 'update',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)


@receiver(post_delete, sender=Price_Additional_Hour)
def log_delete_price_additional_hour(sender, instance, **kwargs):
    user = get_current_user()
    _log_and_record(user, 'Price_Additional_Hour', 'delete', f'El usuario: {user} eliminó el registro {instance}', instance.id)