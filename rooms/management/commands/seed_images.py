import json
import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from rooms.models import Property


class Command(BaseCommand):
    help = 'Precarga imagenes de propiedades desde seed_data/ si no existen'

    def handle(self, *args, **options):
        seed_dir = os.path.join(settings.BASE_DIR, 'Arriendos-Backend', 'seed_data')
        json_path = os.path.join(seed_dir, 'properties.json')
        photos_dir = os.path.join(seed_dir, 'property_photos')
        media_dir = os.path.join(settings.MEDIA_ROOT, 'property_photos')

        if not os.path.exists(json_path):
            self.stdout.write(self.style.WARNING('No se encontro seed_data/properties.json, saltando'))
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            properties = json.load(f)

        os.makedirs(media_dir, exist_ok=True)

        created = 0
        skipped = 0

        for prop in properties:
            name = prop['name']
            photo_file = prop.get('photo_file')

            if Property.objects.filter(name=name).exists():
                self.stdout.write(f'  Ya existe "{name}", omitiendo')
                skipped += 1
                continue

            photo_path = None
            if photo_file:
                src = os.path.join(photos_dir, photo_file)
                dst = os.path.join(media_dir, photo_file)
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    photo_path = f'property_photos/{photo_file}'
                else:
                    self.stdout.write(self.style.WARNING(f'  Imagen no encontrada: {src}'))

            Property.objects.create(
                name=name,
                address=prop.get('address'),
                department=prop.get('department'),
                photo=photo_path,
            )
            self.stdout.write(self.style.SUCCESS(f'  Propiedad "{name}" creada'))
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Resultado: {created} creadas, {skipped} omitidas'))
