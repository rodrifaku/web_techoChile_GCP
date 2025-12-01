from django.core.management.base import BaseCommand
from incidencias.models import Observacion, ArchivoAdjuntoObservacion


class Command(BaseCommand):
    help = 'Check files for a specific observation'

    def add_arguments(self, parser):
        parser.add_argument('observation_id', type=int, help='Observation ID to check')

    def handle(self, *args, **options):
        obs_id = options['observation_id']
        
        try:
            obs = Observacion.objects.get(pk=obs_id)
            self.stdout.write(self.style.SUCCESS(f'Observación {obs_id} encontrada:'))
            self.stdout.write(f'  ID: {obs.pk}')
            
            if obs.archivo_adjunto:
                self.stdout.write(f'  Archivo principal: {obs.archivo_adjunto.name}')
                self.stdout.write(f'    - Existe: {obs.archivo_existe()}')
                url = obs.get_url_archivo()
                self.stdout.write(f'    - URL: {url if url else "(sin URL)"}')
                size = obs.get_tamaño_archivo()
                self.stdout.write(f'    - Tamaño: {size if size else "(sin tamaño)"}')
            else:
                self.stdout.write('  Archivo principal: (sin archivo principal)')
            
            archivos = ArchivoAdjuntoObservacion.objects.filter(observacion=obs)
            self.stdout.write(f'  Archivos adjuntos: {archivos.count()}')
            
            for archivo in archivos:
                if archivo.archivo:
                    self.stdout.write(f'    - {archivo.archivo.name}')
                    self.stdout.write(f'      Nombre original: {archivo.nombre_original}')
                    self.stdout.write(f'      Existe: {archivo.archivo_existe()}')
                    url = archivo.get_url_archivo()
                    self.stdout.write(f'      URL: {url if url else "(sin URL)"}')
                    size = archivo.get_tamaño_archivo()
                    self.stdout.write(f'      Tamaño: {size if size else "(sin tamaño)"}')
                else:
                    self.stdout.write(f'    - (sin archivo) | Nombre original: {archivo.nombre_original}')
                    
        except Observacion.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'ERROR: Observación {obs_id} no existe en la base de datos'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERROR: {e}'))
