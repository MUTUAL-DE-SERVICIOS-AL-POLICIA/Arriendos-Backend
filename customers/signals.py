import logging
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from records.utils import get_current_user, create_record
from .models import *

business_logger = logging.getLogger('business')


@receiver(post_save, sender=Customer_type)
def log_create_customer_type(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        create_record(user, 'create', 'Customer_type', f'El usuario: {user} creó el registro {instance}', instance.id)
    business_logger.info(f"[CUSTOMER_TYPE] CREATE: {instance} creado (user={user}, id={instance.id})")


@receiver(pre_save, sender=Customer_type)
def log_edit_customer_type(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Customer_type.objects.get(pk=instance.pk)
        except Customer_type.DoesNotExist:
            return
        for field in Customer_type._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                create_record(user, 'update', 'Customer_type',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)
            business_logger.info(f"[CUSTOMER_TYPE] UPDATE: Campo '{field.name}' de '{old_value}' a '{new_value}' en {instance} (user={user})")


@receiver(post_delete, sender=Customer_type)
def log_delete_customer_type(sender, instance, **kwargs):
    user = get_current_user()
    create_record(user, 'delete', 'Customer_type', f'El usuario: {user} eliminó el registro {instance}', instance.id)
    business_logger.info(f"[CUSTOMER_TYPE] DELETE: {instance} eliminado (user={user}, id={instance.id})")


@receiver(post_save, sender=Customer)
def log_create_customer(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        create_record(user, 'create', 'Customer', f'El usuario: {user} creó el registro {instance}', instance.id)
    business_logger.info(f"[CUSTOMER] CREATE: {instance} creado (user={user}, id={instance.id})")


@receiver(pre_save, sender=Customer)
def log_edit_customer(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Customer.objects.get(pk=instance.pk)
        except Customer.DoesNotExist:
            return
        for field in Customer._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                create_record(user, 'update', 'Customer',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)
            business_logger.info(f"[CUSTOMER] UPDATE: Campo '{field.name}' de '{old_value}' a '{new_value}' en {instance} (user={user})")


@receiver(post_delete, sender=Customer)
def log_delete_customer(sender, instance, **kwargs):
    user = get_current_user()
    create_record(user, 'delete', 'Customer', f'El usuario: {user} eliminó el registro {instance}', instance.id)
    business_logger.info(f"[CUSTOMER] DELETE: {instance} eliminado (user={user}, id={instance.id})")


@receiver(post_save, sender=Contact)
def log_create_contact(sender, instance, created, **kwargs):
    user = get_current_user()
    if created:
        create_record(user, 'create', 'Contact', f'El usuario: {user} creó el registro {instance}', instance.id)
    business_logger.info(f"[CONTACT] CREATE: {instance} creado (user={user}, id={instance.id})")


@receiver(pre_save, sender=Contact)
def log_edit_contact(sender, instance, **kwargs):
    if instance.pk is not None:
        user = get_current_user()
        try:
            old_instance = Contact.objects.get(pk=instance.pk)
        except Contact.DoesNotExist:
            return
        for field in Contact._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                create_record(user, 'update', 'Contact',
                    f'El usuario: {user} realizó un cambio en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}',
                    instance.id)
            business_logger.info(f"[CONTACT] UPDATE: Campo '{field.name}' de '{old_value}' a '{new_value}' en {instance} (user={user})")


@receiver(post_delete, sender=Contact)
def log_delete_contact(sender, instance, **kwargs):
    user = get_current_user()
    create_record(user, 'delete', 'Contact', f'El usuario: {user} eliminó el registro {instance}', instance.id)
    business_logger.info(f"[CONTACT] DELETE: {instance} eliminado (user={user}, id={instance.id})")
