from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from users.models import Record
from threadlocals.threadlocals import get_thread_variable
from .models import *

@receiver(post_save, sender=Room)
def log_create_room(sender, instance, created, **kwargs):
    model="Room"
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
@receiver(pre_save, sender=Room)
def log_edit_user(sender, instance, **kwargs):
    action="update"
    model="Room"
    if instance.pk is not None:
        old_instance = Room.objects.get(pk=instance.pk)
        for field in Room._meta.fields:
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
@receiver(post_delete, sender=Room)
def log_delete_room(sender, instance, **kwargs):
    model="Room"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}"
    )

@receiver(post_save, sender=Property)
def log_create_property(sender, instance, created, **kwargs):
    model="Property"
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
@receiver(pre_save, sender=Property)
def log_edit_property(sender, instance, **kwargs):
    action="update"
    model="Property"
    if instance.pk is not None:
        old_instance = Room.objects.get(pk=instance.pk)
        for field in Room._meta.fields:
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
@receiver(post_delete, sender=Property)
def log_delete_property(sender, instance, **kwargs):
    model="Property"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}"
    )

@receiver(post_save, sender=Sub_Environment)
def log_create_sub_enviroment(sender, instance, created, **kwargs):
    model="Sub_Environment"
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
@receiver(pre_save, sender=Sub_Environment)
def log_edit_sub_enviroment(sender, instance, **kwargs):
    action="update"
    model="Sub_Environment"
    if instance.pk is not None:
        old_instance = Sub_Environment.objects.get(pk=instance.pk)
        for field in Sub_Environment._meta.fields:
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
@receiver(post_delete, sender=Sub_Environment)
def log_delete_sub_enviroment(sender, instance, **kwargs):
    model="Sub_Environment"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}"
    )