from django.db.models.signals import post_save, pre_save, post_delete
from threadlocals.threadlocals import get_thread_variable
from django.dispatch import receiver
from users.models import Record
from .models import *

@receiver(post_save, sender=Payment)
def log_create_payment(sender, instance, created, **kwargs):
    model="Payment"
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
                Record.objects.create(
                    user=user,
                    action=action,
                    model=model,
                    detail=f'El usuario: {user} realizó un cambió en el campo {field.name}: del anterior valor: {old_value}, al nuevo valor: {new_value} del registro: {instance}'
                )
@receiver(post_delete, sender=Payment)
def log_delete_payment(sender, instance, **kwargs):
    model="Payment"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}"
    )