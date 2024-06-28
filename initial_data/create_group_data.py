import os
import sys
import django

sys.path.append('/app')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Arriendos_Backend.settings")
django.setup()

from django.contrib.auth.models import Group, Permission

def create_group_with_all_permissions(group_name):
    group, created = Group.objects.get_or_create(name=group_name)
    permissions = Permission.objects.all()
    group.permissions.set(permissions)
    group.save()
    print(f"Grupo '{group_name}' ha sido creado y se le han asignado todos los permisos.")
if __name__ == "__main__":
    create_group_with_all_permissions('AllPermissionsGroup')