"""
Utilidad de auditoría para cambios RBAC.

Registra acciones de seguridad en el modelo Record:
- Quién realizó la acción
- Qué acción realizó
- Cuándo ocurrió
- Detalles de la operación

Acciones registradas:
- ROLE_CREATE: Creación de un nuevo rol
- ROLE_UPDATE: Modificación de un rol existente
- ROLE_DELETE: Eliminación de un rol
- ROLE_ASSIGN: Asignación de rol a usuario
- ROLE_REMOVE: Remoción de rol de usuario
- USER_UPDATE: Modificación de datos de usuario
- USER_ACTIVATE: Activación de usuario
- USER_DEACTIVATE: Desactivación de usuario

Autor: Dilan Torrez
Fecha: 2026
"""

import logging
from .models import Record

security_logger = logging.getLogger('security')


def create_rbac_audit(user, action, detail, instance_id=None):
    """
    Registra una acción de auditoría RBAC en el modelo Record.

    @param user: Usuario que realizó la acción (User object o None)
    @param action: Tipo de acción (ROLE_CREATE, ROLE_ASSIGN, etc.)
    @param detail: Descripción legible de la acción
    @param instance_id: ID de la instancia afectada (opcional)
    """
    try:
        Record.objects.create(
            user=user,
            action=action,
            model="RBAC",
            detail=detail,
            instance_id=instance_id,
        )
        security_logger.info(
            f"RBAC_AUDIT: user={user.username if user else 'system'} "
            f"action={action} detail={detail}"
        )
    except Exception as e:
        security_logger.error(f"RBAC_AUDIT_ERROR: {str(e)}")
