from django.core.management.base import BaseCommand
from lumenApp.models import Rol, TipoCulto

class Command(BaseCommand):
    help = 'Crea roles, tipos de culto '

    def handle(self, *args, **options):
        # Roles
        roles = [
            'Capataz',
            'Costalero',
            'Acolito',
            'Auxiliares',
            'Diputado de formación',
            'Diputado Mayor de gobierno',
            'Secretario',
            'Mayordomo',
            'Fiscal',
            'Promotora sacramental',
            'Teniente Hermano Mayor',
            'Hermano Mayor'
        ]
        for r in roles:
            Rol.objects.get_or_create(nombre=r)

        self.stdout.write(self.style.SUCCESS('Roles creados correctamente.'))

        # Tipos de culto
        tipos_culto = [
            'Culto Eucarístico',
            'Vigilia',
            'Acto Solemnes',
            'Estación de penitencia',
            'Besamanos',
            'Triduo',
            'Misa'
        ]
        for t in tipos_culto:
            TipoCulto.objects.get_or_create(nombre=t)

        self.stdout.write(self.style.SUCCESS('Tipos de culto creados correctamente.'))
