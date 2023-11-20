from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from users.models import Record
from .models import State, Rental, Event_Type, Selected_Product, Additional_Hour_Applied
from threadlocals.threadlocals import get_thread_variable
@receiver(post_save, sender=State)
def log_create_state(sender, instance, created, **kwargs):
    model="State"
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
@receiver(pre_save, sender=State)
def log_edit_state(sender, instance, **kwargs):
    action="update"
    model="State"
    if instance.pk is not None:
        old_instance = State.objects.get(pk=instance.pk)
        for field in State._meta.fields:
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
@receiver(post_delete, sender=State)
def log_delete_state(sender, instance, **kwargs):
    model="State"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}"
    )
@receiver(post_save, sender=Rental)
def log_create_rental(sender, instance, created, **kwargs):
    model="Rental"
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
@receiver(pre_save, sender=Rental)
def log_edit_rental(sender, instance, **kwargs):
    action="update"
    model="Rental"
    if instance.pk is not None:
        old_instance = Rental.objects.get(pk=instance.pk)
        for field in Rental._meta.fields:
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
@receiver(post_delete, sender=Rental)
def log_delete_rental(sender, instance, **kwargs):
    model="Rental"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}"
    )
@receiver(post_save, sender=Event_Type)
def log_create_event_type(sender, instance, created, **kwargs):
    model="Event_Type"
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
@receiver(pre_save, sender=Event_Type)
def log_edit_event_type(sender, instance, **kwargs):
    action="update"
    model="Event_Type"
    if instance.pk is not None:
        old_instance = Event_Type.objects.get(pk=instance.pk)
        for field in Event_Type._meta.fields:
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
@receiver(post_delete, sender=Event_Type)
def log_delete_event_type(sender, instance, **kwargs):
    model="Event_Type"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}"
    )
@receiver(post_save, sender=Selected_Product)
def log_create_selected_product(sender, instance, created, **kwargs):
    model="Selected_Product"
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
@receiver(pre_save, sender=Selected_Product)
def log_edit_selected_product(sender, instance, **kwargs):
    action="update"
    model="Selected_Product"
    if instance.pk is not None:
        old_instance = Selected_Product.objects.get(pk=instance.pk)
        for field in Selected_Product._meta.fields:
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
@receiver(post_delete, sender=Selected_Product)
def log_delete_selected_product(sender, instance, **kwargs):
    model="Selected_Product"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}"
    )
@receiver(post_save, sender=Additional_Hour_Applied)
def log_create_additional_hour_applied(sender, instance, created, **kwargs):
    model="Additional_Hour_Applied"
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
@receiver(pre_save, sender=Additional_Hour_Applied)
def log_edit_additional_hour_applied(sender, instance, **kwargs):
    action="update"
    model="Additional_Hour_Applied"
    if instance.pk is not None:
        old_instance = Additional_Hour_Applied.objects.get(pk=instance.pk)
        for field in Additional_Hour_Applied._meta.fields:
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
@receiver(post_delete, sender=Additional_Hour_Applied)
def log_delete_additional_hour_applied(sender, instance, **kwargs):
    model="Additional_Hour_Applied"
    user = get_thread_variable('thread_user')
    action="delete"
    Record.objects.create(
        user=user,
        action=action,
        model=model,
        detail=f"El usuario: {user} eliminó el registro {instance}"
    )