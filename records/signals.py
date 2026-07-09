"""
Signals para registrar auditoria de roles, permisos y login.

Captura cambios en:
- Role (crear, editar, eliminar)
- RolePermission (cambiar permisos de rol)
- UserRole (asignar/quitar rol a usuario)

Autor: Dilan Torrez
Fecha: 2026
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from threadlocals.threadlocals import get_thread_variable

from roles.models import Role, RolePermission, UserRole

business_logger = logging.getLogger('business')
security_logger = logging.getLogger('security')


def get_current_user():
    return get_thread_variable('thread_user')


def create_record(user, action, model, instance_id, detail):
    from users.models import Record
    try:
        Record.objects.create(
            user=user,
            action=action,
            model=model,
            detail=detail,
            instance_id=instance_id
        )
    except Exception as e:
        business_logger.error(f"[RECORD] Audit record failed: {e}")


@receiver(post_save, sender=Role)
def role_post_save(sender, instance, created, **kwargs):
    user = get_current_user()
    action = 'create' if created else 'update'
    detail = f"Rol '{instance.name}' {'creado' if created else 'actualizado'}"
    create_record(user, action, 'Role', instance.id, detail)
    business_logger.info(f"ROLE_{action.upper()}: {instance.name} (id={instance.id})")


@receiver(post_delete, sender=Role)
def role_post_delete(sender, instance, **kwargs):
    user = get_current_user()
    detail = f"Rol '{instance.name}' eliminado"
    create_record(user, 'delete', 'Role', instance.id, detail)
    business_logger.info(f"ROLE_DELETE: {instance.name} (id={instance.id})")


@receiver(post_save, sender=RolePermission)
def role_permission_post_save(sender, instance, created, **kwargs):
    user = get_current_user()
    perms = ', '.join([p.codename for p in instance.permissions.all()])
    action = 'create' if created else 'update'
    detail = f"Permisos de rol '{instance.role.name}' en '{instance.module.name}': [{perms}]"
    create_record(user, action, 'RolePermission', instance.id, detail)
    business_logger.info(f"ROLEPERMISSION_{action.upper()}: {instance.role.name} -> {instance.module.name} = [{perms}]")


@receiver(post_delete, sender=RolePermission)
def role_permission_post_delete(sender, instance, **kwargs):
    user = get_current_user()
    detail = f"Permisos eliminados: rol '{instance.role.name}' en '{instance.module.name}'"
    create_record(user, 'delete', 'RolePermission', instance.id, detail)
    business_logger.info(f"ROLEPERMISSION_DELETE: {instance.role.name} -> {instance.module.name}")


@receiver(post_save, sender=UserRole)
def user_role_post_save(sender, instance, created, **kwargs):
    user = get_current_user()
    action = 'create' if created else 'update'
    detail = f"Rol '{instance.role.name}' asignado a usuario '{instance.user.username}'"
    create_record(user, action, 'UserRole', instance.id, detail)
    business_logger.info(f"USERROLE_{action.upper()}: {instance.user.username} -> {instance.role.name}")


@receiver(post_delete, sender=UserRole)
def user_role_post_delete(sender, instance, **kwargs):
    user = get_current_user()
    detail = f"Rol '{instance.role.name}' removido de usuario '{instance.user.username}'"
    create_record(user, 'delete', 'UserRole', instance.id, detail)
    business_logger.info(f"USERROLE_DELETE: {instance.user.username} -> {instance.role.name}")


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created:
        user = get_current_user()
        detail = f"Usuario '{instance.username}' creado"
        create_record(user, 'create', 'User', instance.id, detail)
        business_logger.info(f"USER_CREATE: {instance.username}")


@receiver(post_delete, sender=User)
def user_post_delete(sender, instance, **kwargs):
    user = get_current_user()
    detail = f"Usuario '{instance.username}' eliminado"
    create_record(user, 'delete', 'User', instance.id, detail)
    business_logger.info(f"USER_DELETE: {instance.username}")
