from django.core.management.base import BaseCommand
from core.models import LeituraOCR

class Command(BaseCommand):
    help = "Recalcula o consumo entre leituras para as leituras antigas."

    def handle(self, *args, **kwargs):
        leituras = LeituraOCR.objects.all().order_by('estado', 'data_registro')

        # Armazenar a última leitura para cada estado
        estados_ultimas_leituras = {}

        for leitura in leituras:
            estado_id = leitura.estado_id
            ultima_leitura = estados_ultimas_leituras.get(estado_id)

            if ultima_leitura:
                # Calcular a diferença de consumo entre a leitura atual e a anterior
                consumo = leitura.valor_corrigido - ultima_leitura.valor_corrigido
                print(f"Consumo entre leituras para estado {estado_id}: {consumo}")  # Debug

                # Garantir que o consumo não seja negativo
                leitura.consumo_entre_leituras = consumo if consumo >= 0 else 0
            else:
                leitura.consumo_entre_leituras = 0  # Primeira leitura para esse estado

            print(f"Leitura {leitura.id} - Consumo entre leituras: {leitura.consumo_entre_leituras}")  # Debug

            leitura.save()
            estados_ultimas_leituras[estado_id] = leitura

        self.stdout.write(self.style.SUCCESS('Consumos recalculados com sucesso para leituras antigas.'))
