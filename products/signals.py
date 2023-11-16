from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from users.models import Record
from .models import Rate, HourRange, Product, Price, Price_Additional_Hour
from threadlocals.threadlocals import get_thread_variable
@receiver(post_save, sender=Rate)
def log_create_user(sender, instance, created, **kwargs):
    model="Rate"
    user = get_thread_variable('thread_user')
    if created:
        detail=f"El usuario: {user} creó el registro {instance}"
        action="create"
        Record.objects.create(
            user=user,
            action=action,
            model=model,
            detail=detail
        )
@receiver(pre_save, sender=Rate)
def log_edit_user(sender, instance, **kwargs):
    action="update"
    model="Rate"
    if instance.pk is not None:
        old_instance = Rate.objects.get(pk=instance.pk)
        for field in Rate._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            user = get_thread_variable('thread_user')
            if old_value != new_value:
                Record.objects.create(
                    user=user,
                    action=action,
                    model=model,
                    detail=f'El usuario: {user} realizó un cambió en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}'
                )
@receiver(post_delete, sender=Rate)
def log_delete_user(sender, instance, **kwargs):
    model="Rate"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}"
    )
@receiver(post_save, sender=HourRange)
def log_create_user(sender, instance, created, **kwargs):
    model="HourRange"
    user = get_thread_variable('thread_user')
    if created:
        detail=f"El usuario: {user} creó el registro {instance}"
        action="create"
        Record.objects.create(
            user=user,
            action=action,
            model=model,
            detail=detail
        )
@receiver(pre_save, sender=HourRange)
def log_edit_user(sender, instance, **kwargs):
    action="update"
    model="HourRange"
    if instance.pk is not None:
        old_instance = HourRange.objects.get(pk=instance.pk)
        for field in HourRange._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            user = get_thread_variable('thread_user')
            if old_value != new_value:
                Record.objects.create(
                    user=user,
                    action=action,
                    model=model,
                    detail=f'El usuario: {user} realizó un cambió en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}'
                )
@receiver(post_delete, sender=HourRange)
def log_delete_user(sender, instance, **kwargs):
    model="HourRange"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}"
    )
@receiver(post_save, sender=Product)
def log_create_user(sender, instance, created, **kwargs):
    model="Product"
    user = get_thread_variable('thread_user')
    if created:
        detail=f"El usuario: {user} creó el registro {instance}"
        action="create"
        Record.objects.create(
            user=user,
            action=action,
            model=model,
            detail=detail
        )
@receiver(pre_save, sender=Product)
def log_edit_user(sender, instance, **kwargs):
    action="update"
    model="Product"
    if instance.pk is not None:
        old_instance = Product.objects.get(pk=instance.pk)
        for field in Product._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            user = get_thread_variable('thread_user')
            if old_value != new_value:
                Record.objects.create(
                    user=user,
                    action=action,
                    model=model,
                    detail=f'El usuario: {user} realizó un cambió en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}'
                )
@receiver(post_delete, sender=Product)
def log_delete_user(sender, instance, **kwargs):
    model="Product"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}"
    )
@receiver(post_save, sender=Price)
def log_create_user(sender, instance, created, **kwargs):
    model="Price"
    user = get_thread_variable('thread_user')
    if created:
        detail=f"El usuario: {user} creó el registro {instance}"
        action="create"
        Record.objects.create(
            user=user,
            action=action,
            model=model,
            detail=detail
        )
@receiver(pre_save, sender=Price)
def log_edit_user(sender, instance, **kwargs):
    action="update"
    model="Price"
    if instance.pk is not None:
        old_instance = Price.objects.get(pk=instance.pk)
        for field in Price._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            user = get_thread_variable('thread_user')
            if old_value != new_value:
                Record.objects.create(
                    user=user,
                    action=action,
                    model=model,
                    detail=f'El usuario: {user} realizó un cambió en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}'
                )
@receiver(post_delete, sender=Price)
def log_delete_user(sender, instance, **kwargs):
    model="Price"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}"
    )
@receiver(post_save, sender=Price_Additional_Hour)
def log_create_user(sender, instance, created, **kwargs):
    model="Price_Additional_Hour"
    user = get_thread_variable('thread_user')
    if created:
        detail=f"El usuario: {user} creó el registro {instance}"
        action="create"
        Record.objects.create(
            user=user,
            action=action,
            model=model,
            detail=detail
        )
@receiver(pre_save, sender=Price_Additional_Hour)
def log_edit_user(sender, instance, **kwargs):
    action="update"
    model="Price_Additional_Hour"
    if instance.pk is not None:
        old_instance = Price_Additional_Hour.objects.get(pk=instance.pk)
        for field in Price_Additional_Hour._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            user = get_thread_variable('thread_user')
            if old_value != new_value:
                Record.objects.create(
                    user=user,
                    action=action,
                    model=model,
                    detail=f'El usuario: {user} realizó un cambió en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}'
                )
@receiver(post_delete, sender=Price_Additional_Hour)
def log_delete_user(sender, instance, **kwargs):
    model="Price_Additional_Hour"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}"
    )