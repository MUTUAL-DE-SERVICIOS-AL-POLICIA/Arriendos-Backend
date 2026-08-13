import os
from django.core.management.base import BaseCommand
from roles.models import Module, Permission, Role, RolePermission, UserRole
from django.contrib.auth import get_user_model
User = get_user_model()


class Command(BaseCommand):
    help = 'Crea los modulos, permisos y roles iniciales del sistema RBAC'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando creacion de RBAC...'))

        modules_data = [
            {'name': 'Productos', 'codename': 'products', 'description': 'Gestion de productos, tarifas, precios'},
            {'name': 'Inmuebles', 'codename': 'rooms', 'description': 'Gestion de inmuebles y ambientes'},
            {'name': 'Clientes', 'codename': 'customers', 'description': 'Gestion de clientes y tipos de cliente'},
            {'name': 'Arriendos', 'codename': 'leases', 'description': 'Gestion de arriendos y reservas'},
            {'name': 'Finanzas', 'codename': 'financials', 'description': 'Gestion de pagos y garantias'},
            {'name': 'Requisitos', 'codename': 'requirements', 'description': 'Gestion de requisitos'},
            {'name': 'Usuarios', 'codename': 'users', 'description': 'Gestion de usuarios y roles del sistema'},
            {'name': 'Registros', 'codename': 'records', 'description': 'Consulta de registros de cambios del sistema'},
            {'name': 'Documentos', 'codename': 'documents', 'description': 'Acceso a documentos PDF, Excel y reportes'},
        ]

        permissions_data = [
            {'name': 'Ver', 'codename': 'view'},
            {'name': 'Crear', 'codename': 'add'},
            {'name': 'Editar', 'codename': 'change'},
            {'name': 'Eliminar', 'codename': 'delete'},
        ]

        modules = {}
        for md in modules_data:
            module, _ = Module.objects.get_or_create(
                codename=md['codename'],
                defaults={'name': md['name'], 'description': md['description']}
            )
            modules[md['codename']] = module
            self.stdout.write(f'  Modulo: {module.name}')

        permissions = {}
        for pd in permissions_data:
            perm, _ = Permission.objects.get_or_create(
                codename=pd['codename'],
                defaults={'name': pd['name']}
            )
            permissions[pd['codename']] = perm
            self.stdout.write(f'  Permiso: {perm.name}')

        roles_config = {
            'Administrador': {
                'description': 'Acceso total al sistema',
                'modules': {m: list(permissions.values()) for m in modules.values()},
            },
            'Operador': {
                'description': 'Operaciones diarias de arriendos',
                'modules': {
                    modules['products']: [permissions['view']],
                    modules['rooms']: [permissions['view']],
                    modules['customers']: [permissions['view'], permissions['add']],
                    modules['leases']: [permissions['view'], permissions['add'], permissions['change']],
                    modules['financials']: [permissions['view']],
                    modules['requirements']: [permissions['view']],
                },
            },
            'Visualizador': {
                'description': 'Solo lectura en todo el sistema',
                'modules': {m: [permissions['view']] for m in modules.values()},
            },
        }

        for role_name, config in roles_config.items():
            role, _ = Role.objects.get_or_create(
                name=role_name,
                defaults={'description': config['description']}
            )
            self.stdout.write(f'  Rol: {role.name}')

            RolePermission.objects.filter(role=role).delete()
            for module, perms in config['modules'].items():
                rp = RolePermission.objects.create(role=role, module=module)
                rp.permissions.set(perms)

        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin_user.set_password(admin_password)
            admin_user.save()
            self.stdout.write(f'  Usuario admin creado')

        admin_role = Role.objects.get(name='Administrador')
        UserRole.objects.get_or_create(user=admin_user, defaults={'role': admin_role})
        self.stdout.write(f'  Rol Administrador asignado a admin')

        self.stdout.write(self.style.SUCCESS('RBAC inicializado correctamente!'))
