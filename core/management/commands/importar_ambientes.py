from django.core.management.base import BaseCommand
from core.models import Ambiente

DADOS_AMBIENTES = [
    "Quarto",
    "Sala",
    "Cozinha",
    "Banheiro",
    "Escritório",
    "Lavanderia",
    "Garagem",
    "Área externa",
]

class Command(BaseCommand):
    help = 'Importa os ambientes padrão para o sistema'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando importação de ambientes...")

        for nome in DADOS_AMBIENTES:
            ambiente, created = Ambiente.objects.get_or_create(nome=nome)
            self.stdout.write(f"Ambiente {'criado' if created else 'já existia'}: {ambiente.nome}")

        self.stdout.write(self.style.SUCCESS("Importação de ambientes concluída com sucesso!"))
