from django.core.management.base import BaseCommand
from reportes.models import ReporteGenerado


class Command(BaseCommand):
    help = 'Elimina reportes que no tienen archivo en GCS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué se eliminaría sin hacerlo',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Buscar reportes sin archivo
        reportes_sin_archivo = ReporteGenerado.objects.filter(archivo='')
        total = reportes_sin_archivo.count()

        if dry_run:
            self.stdout.write(self.style.WARNING(f'[DRY RUN] Se eliminarían {total} reportes sin archivo:'))
        else:
            self.stdout.write(f'Eliminando {total} reportes sin archivo...')

        for reporte in reportes_sin_archivo:
            msg = f'ID {reporte.id}: {reporte.nombre_archivo} - {reporte.fecha_generacion}'
            if dry_run:
                self.stdout.write(self.style.WARNING(f'  - {msg}'))
            else:
                reporte.delete()
                self.stdout.write(self.style.SUCCESS(f'  ✓ Eliminado: {msg}'))

        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f'\n✓ {total} reportes eliminados correctamente'))
        else:
            self.stdout.write(self.style.WARNING(f'\n[DRY RUN] Se eliminarían {total} reportes'))
            self.stdout.write(self.style.WARNING('Ejecuta sin --dry-run para eliminar'))
