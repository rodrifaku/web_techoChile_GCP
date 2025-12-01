from django.core.management.base import BaseCommand
from incidencias.models import Observacion, ArchivoAdjuntoObservacion


class Command(BaseCommand):
    help = 'List all file paths in database and check if they exist in GCS'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Verificando archivos de observaciones...'))
        
        # Archivos principales de observaciones
        obs_con_archivo = Observacion.objects.exclude(archivo_adjunto='')
        self.stdout.write(f'\nArchivos principales en observaciones: {obs_con_archivo.count()}')
        
        missing_principal = []
        for obs in obs_con_archivo:
            if obs.archivo_adjunto:
                path = obs.archivo_adjunto.name
                exists = obs.archivo_existe()
                if not exists:
                    missing_principal.append((obs.pk, path))
                    self.stdout.write(f'  ❌ Obs {obs.pk}: {path} (NO EXISTE)')
        
        # Archivos adjuntos adicionales
        archivos = ArchivoAdjuntoObservacion.objects.all()
        self.stdout.write(f'\nArchivos adjuntos adicionales: {archivos.count()}')
        
        missing_adjuntos = []
        for archivo in archivos:
            if archivo.archivo:
                path = archivo.archivo.name
                exists = archivo.archivo_existe()
                if not exists:
                    missing_adjuntos.append((archivo.observacion_id, path))
                    self.stdout.write(f'  ❌ Obs {archivo.observacion_id}: {path} (NO EXISTE)')
        
        # Resumen
        self.stdout.write(self.style.SUCCESS(f'\n📊 RESUMEN:'))
        self.stdout.write(f'  Archivos principales faltantes: {len(missing_principal)}')
        self.stdout.write(f'  Archivos adjuntos faltantes: {len(missing_adjuntos)}')
        total_missing = len(missing_principal) + len(missing_adjuntos)
        self.stdout.write(f'  TOTAL FALTANTE: {total_missing}')
