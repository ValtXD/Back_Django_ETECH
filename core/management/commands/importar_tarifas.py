from django.core.management.base import BaseCommand
from core.models import Estado, Tarifa, Bandeira, TarifaSocial

DADOS_ESTADOS = [
    {"nome": "Pará", "sigla": "PA", "tarifa": 0.938},
    {"nome": "Mato Grosso do Sul", "sigla": "MS", "tarifa": 0.870},
    {"nome": "Rio de Janeiro", "sigla": "RJ", "tarifa": 0.870},
    {"nome": "Alagoas", "sigla": "AL", "tarifa": 0.863},
    {"nome": "Amazonas", "sigla": "AM", "tarifa": 0.857},
    {"nome": "Mato Grosso", "sigla": "MT", "tarifa": 0.847},
    {"nome": "Piauí", "sigla": "PI", "tarifa": 0.829},
    {"nome": "Tocantins", "sigla": "TO", "tarifa": 0.823},
    {"nome": "Bahia", "sigla": "BA", "tarifa": 0.821},
    {"nome": "Amapá", "sigla": "AP", "tarifa": 0.808},
    {"nome": "Minas Gerais", "sigla": "MG", "tarifa": 0.796},
    {"nome": "Acre", "sigla": "AC", "tarifa": 0.791},
    {"nome": "Goiás", "sigla": "GO", "tarifa": 0.745},
    {"nome": "Pernambuco", "sigla": "PE", "tarifa": 0.744},
    {"nome": "Distrito Federal", "sigla": "DF", "tarifa": 0.743},
    {"nome": "Rondônia", "sigla": "RO", "tarifa": 0.727},
    {"nome": "Ceará", "sigla": "CE", "tarifa": 0.722},
    {"nome": "Rio Grande do Norte", "sigla": "RN", "tarifa": 0.722},
    {"nome": "Maranhão", "sigla": "MA", "tarifa": 0.711},
    {"nome": "Rio Grande do Sul", "sigla": "RS", "tarifa": 0.701},
    {"nome": "Espírito Santo", "sigla": "ES", "tarifa": 0.682},
    {"nome": "São Paulo", "sigla": "SP", "tarifa": 0.671},
    {"nome": "Sergipe", "sigla": "SE", "tarifa": 0.666},
    {"nome": "Roraima", "sigla": "RR", "tarifa": 0.661},
    {"nome": "Paraná", "sigla": "PR", "tarifa": 0.629},
    {"nome": "Santa Catarina", "sigla": "SC", "tarifa": 0.618},
    {"nome": "Paraíba", "sigla": "PB", "tarifa": 0.588},
]

DADOS_BANDEIRAS = [
    {
        "cor": "verde",
        "valor_adicional": 0.0,
        "descricao": "Condições favoráveis de geração de energia. A tarifa não sofre nenhum acréscimo."
    },
    {
        "cor": "amarela",
        "valor_adicional": 0.01885,
        "descricao": "Condições de geração menos favoráveis. A tarifa sofre acréscimo de R$ 0,01885 para cada quilowatt-hora (kWh) consumidos."
    },
    {
        "cor": "vermelha1",
        "valor_adicional": 0.04463,
        "descricao": "Condições mais custosas de geração. A tarifa sofre acréscimo de R$ 0,04463 para cada quilowatt-hora kWh consumido."
    },
    {
        "cor": "vermelha2",
        "valor_adicional": 0.07877,
        "descricao": "Condições ainda mais custosas de geração. A tarifa sofre acréscimo de R$ 0,07877 para cada quilowatt-hora kWh consumido."
    }
]

DADOS_TARIFA_SOCIAL = [
    {
        "faixa_consumo": "Até 30 kWh",
        "desconto_percentual": 65.0,
        "descricao": "65% de desconto para consumo mensal de até 30 kWh"
    },
    {
        "faixa_consumo": "31 kWh a 100 kWh",
        "desconto_percentual": 40.0,
        "descricao": "40% de desconto para consumo mensal entre 31 kWh e 100 kWh"
    },
    {
        "faixa_consumo": "101 kWh a 220 kWh",
        "desconto_percentual": 10.0,
        "descricao": "10% de desconto para consumo mensal entre 101 kWh e 220 kWh"
    },
    {
        "faixa_consumo": "Acima de 220 kWh",
        "desconto_percentual": 0.0,
        "descricao": "Sem desconto para consumo mensal acima de 220 kWh"
    }
]


class Command(BaseCommand):
    help = 'Importa dados iniciais de tarifas por estado, bandeiras tarifárias e tarifa social'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando importação de dados...")

        # Importar estados e tarifas
        for dados_estado in DADOS_ESTADOS:
            estado, created = Estado.objects.get_or_create(
                nome=dados_estado["nome"],
                defaults={"sigla": dados_estado["sigla"]}
            )

            if created:
                self.stdout.write(f"Estado criado: {estado.nome} ({estado.sigla})")

            tarifa, created = Tarifa.objects.update_or_create(
                estado=estado,
                defaults={"valor_kwh": dados_estado["tarifa"]}
            )

            self.stdout.write(
                f"Tarifa {'criada' if created else 'atualizada'}: {tarifa.estado.nome} - R$ {tarifa.valor_kwh}/kWh")

        # Importar bandeiras
        for dados_bandeira in DADOS_BANDEIRAS:
            bandeira, created = Bandeira.objects.update_or_create(
                cor=dados_bandeira["cor"],
                defaults={
                    "valor_adicional": dados_bandeira["valor_adicional"],
                    "descricao": dados_bandeira["descricao"]
                }
            )

            self.stdout.write(
                f"Bandeira {'criada' if created else 'atualizada'}: {bandeira.get_cor_display()} - R$ {bandeira.valor_adicional}/kWh")

        # Importar tarifa social
        for dados_tarifa in DADOS_TARIFA_SOCIAL:
            tarifa_social, created = TarifaSocial.objects.update_or_create(
                faixa_consumo=dados_tarifa["faixa_consumo"],
                defaults={
                    "desconto_percentual": dados_tarifa["desconto_percentual"],
                    "descricao": dados_tarifa["descricao"]
                }
            )

            self.stdout.write(
                f"Tarifa Social {'criada' if created else 'atualizada'}: {tarifa_social.faixa_consumo} - {tarifa_social.desconto_percentual}%")

        self.stdout.write(self.style.SUCCESS("Importação concluída com sucesso!"))