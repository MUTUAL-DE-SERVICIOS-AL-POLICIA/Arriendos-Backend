from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Plan
from users.models import Record
from threadlocals.threadlocals import get_thread_variable
@receiver(post_save, sender=Plan)
def log_create_plan(sender, instance, created, **kwargs):
    model="Plan"
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
@receiver(pre_save, sender=Plan)
def log_edit_plan(sender, instance, **kwargs):
    action="update"
    model="Plan"
    if instance.pk is not None:
        old_instance = Plan.objects.get(pk=instance.pk)
        for field in Plan._meta.fields:
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
@receiver(post_delete, sender=Plan)
def log_delete_plan(sender, instance, **kwargs):
    model="Plan"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}"
    )