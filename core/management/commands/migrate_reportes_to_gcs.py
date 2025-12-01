from django.core.management.base import BaseCommand
from reportes.models import ReporteGenerado
from django.core.files.storage import default_storage
import os


class Command(BaseCommand):
    help = 'Migra los reportes existentes para usar el campo archivo de GCS'

    def handle(self, *args, **options):
        reportes = ReporteGenerado.objects.filter(archivo='')
        total = reportes.count()
        actualizados = 0
        errores = 0

        self.stdout.write(f"Encontrados {total} reportes sin campo archivo asignado")

        for reporte in reportes:
            try:
                # El nombre del archivo está en nombre_archivo (ej: reporte_techoChile_20251028_0105.pdf)
                nombre = reporte.nombre_archivo
                ruta_gcs = f'reportes/{nombre}'
                
                # Verificar si existe en GCS
                if default_storage.exists(ruta_gcs):
                    # Asignar el campo archivo
                    reporte.archivo = ruta_gcs
                    reporte.save(update_fields=['archivo'])
                    actualizados += 1
                    self.stdout.write(self.style.SUCCESS(f'✓ {reporte.id}: {nombre} -> {ruta_gcs}'))
                else:
                    errores += 1
                    self.stdout.write(self.style.WARNING(f'✗ {reporte.id}: {nombre} no encontrado en GCS'))
            except Exception as e:
                errores += 1
                self.stdout.write(self.style.ERROR(f'✗ {reporte.id}: Error - {e}'))

        self.stdout.write(self.style.SUCCESS(f'\nResumen:'))
        self.stdout.write(f'  Total reportes: {total}')
        self.stdout.write(f'  Actualizados: {actualizados}')
        self.stdout.write(f'  Errores: {errores}')
