from django.core.management.base import BaseCommand
from reportes.models import ReporteGenerado
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = 'Actualiza reportes 27-43 con sus archivos en GCS'

    def handle(self, *args, **options):
        # Reportes del 27 al 43
        reportes = ReporteGenerado.objects.filter(id__gte=27, id__lte=43)
        total = reportes.count()
        actualizados = 0
        errores = 0

        self.stdout.write(f"Encontrados {total} reportes entre IDs 27-43")

        for reporte in reportes:
            try:
                # Si ya tiene archivo, saltar
                if reporte.archivo:
                    self.stdout.write(f'⊙ {reporte.id}: Ya tiene archivo asignado: {reporte.archivo}')
                    continue

                # El nombre del archivo está en nombre_archivo
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
                    self.stdout.write(self.style.WARNING(f'✗ {reporte.id}: {nombre} NO encontrado en GCS'))
            except Exception as e:
                errores += 1
                self.stdout.write(self.style.ERROR(f'✗ {reporte.id}: Error - {e}'))

        self.stdout.write(self.style.SUCCESS(f'\nResumen:'))
        self.stdout.write(f'  Total reportes: {total}')
        self.stdout.write(f'  Actualizados: {actualizados}')
        self.stdout.write(f'  Errores: {errores}')
