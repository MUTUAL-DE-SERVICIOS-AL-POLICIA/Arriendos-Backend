from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Requirement, Requirement_Delivered, RateRequirement
from users.models import Record
from threadlocals.threadlocals import get_thread_variable
@receiver(post_save, sender=Requirement)
def log_create_requirement(sender, instance, created, **kwargs):
    model="Requirement"
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
@receiver(pre_save, sender=Requirement)
def log_edit_requirement(sender, instance, **kwargs):
    action="update"
    model="Requirement"
    if instance.pk is not None:
        old_instance = Requirement.objects.get(pk=instance.pk)
        for field in Requirement._meta.fields:
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
@receiver(post_delete, sender=Requirement)
def log_delete_requirement(sender, instance, **kwargs):
    model="Requirement"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}"
    )
@receiver(post_save, sender=Requirement_Delivered)
def log_create_requirement_delivered(sender, instance, created, **kwargs):
    model="Requirement_Delivered"
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
@receiver(pre_save, sender=Requirement_Delivered)
def log_edit_requirement_delivered(sender, instance, **kwargs):
    action="update"
    model="Requirement_Delivered"
    if instance.pk is not None:
        old_instance = Requirement_Delivered.objects.get(pk=instance.pk)
        for field in Requirement_Delivered._meta.fields:
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
@receiver(post_delete, sender=Requirement_Delivered)
def log_delete_requirement_delivered(sender, instance, **kwargs):
    model="Requirement_Delivered"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}"
    )
@receiver(post_save, sender=RateRequirement)
def log_create_rate_requirement(sender, instance, created, **kwargs):
    model="RateRequirement"
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
@receiver(pre_save, sender=RateRequirement)
def log_edit_rate_requirement(sender, instance, **kwargs):
    action="update"
    model="RateRequirement"
    if instance.pk is not None:
        old_instance = RateRequirement.objects.get(pk=instance.pk)
        for field in RateRequirement._meta.fields:
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
@receiver(post_delete, sender=RateRequirement)
def log_delete_rate_requirement(sender, instance, **kwargs):
    model="RateRequirement"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}"
    )