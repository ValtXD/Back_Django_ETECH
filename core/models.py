from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal, ROUND_HALF_UP

User = get_user_model()

class Ambiente(models.Model):
    """Representa um ambiente físico onde os aparelhos estão localizados"""
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Ambiente")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ambiente"
        verbose_name_plural = "Ambientes"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Estado(models.Model):
    """Representa um estado brasileiro com suas tarifas de energia"""
    nome = models.CharField(max_length=100, unique=True, verbose_name="Estado")
    sigla = models.CharField(max_length=2, unique=True, verbose_name="Sigla")

    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.sigla})"


class Tarifa(models.Model):
    """Armazena as tarifas de energia por estado"""
    estado = models.OneToOneField(
        Estado,
        on_delete=models.CASCADE,
        related_name='tarifa',
        verbose_name="Estado"
    )
    valor_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=5,
        validators=[MinValueValidator(Decimal('0.00001'))],
        verbose_name="Valor por kWh (R$)"
    )
    valor_bandeira_verde = models.DecimalField(
        max_digits=6,
        decimal_places=5,
        default=Decimal('0.00000'),
        verbose_name="Adicional Bandeira Verde (R$)"
    )
    atualizado_em = models.DateField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Tarifa"
        verbose_name_plural = "Tarifas"
        ordering = ['estado__nome']

    def __str__(self):
        return f"Tarifa {self.estado} - R$ {self.valor_kwh}/kWh"


class Bandeira(models.Model):
    CORES = (
        ('verde', 'Verde'),
        ('amarela', 'Amarela'),
        ('vermelha1', 'Vermelha - Patamar 1'),
        ('vermelha2', 'Vermelha - Patamar 2'),
    )

    cor = models.CharField(max_length=10, choices=CORES, unique=True)
    valor_adicional = models.DecimalField(max_digits=6, decimal_places=5)
    descricao = models.TextField()

    def __str__(self):
        return f"{self.get_cor_display()} (R$ {self.valor_adicional}/kWh)"

class TarifaSocial(models.Model):
    """Define as faixas de desconto da tarifa social"""
    FAIXAS = (
        ('ate_30', 'Até 30 kWh/mês'),
        ('31_a_100', '31 a 100 kWh/mês'),
        ('101_a_220', '101 a 220 kWh/mês'),
        ('acima_220', 'Acima de 220 kWh/mês'),
    )

    faixa_consumo = models.CharField(
        max_length=20,
        choices=FAIXAS,
        unique=True,
        verbose_name="Faixa de Consumo"
    )
    desconto_percentual = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Desconto Percentual (%)"
    )
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    atualizado_em = models.DateField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Tarifa Social"
        verbose_name_plural = "Tarifas Sociais"
        ordering = ['faixa_consumo']

    def __str__(self):
        return f"Tarifa Social - {self.get_faixa_consumo_display()} ({self.desconto_percentual}%)"

#-----------------Aparelho------------------#

class Aparelho(models.Model):
    """Representa um aparelho elétrico e seus dados de consumo"""
    nome = models.CharField(max_length=100, verbose_name="Nome do Aparelho")
    potencia_watts = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Potência (Watts)"
    )
    tempo_uso_diario_horas = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Tempo de Uso Diário (horas)"
    )
    quantidade = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantidade"
    )
    ambiente = models.ForeignKey(
        Ambiente,
        on_delete=models.CASCADE,
        related_name='aparelhos',
        verbose_name="Ambiente"
    )
    estado = models.ForeignKey(
        Estado,
        on_delete=models.CASCADE,
        related_name='aparelhos',
        verbose_name="Estado"
    )
    bandeira = models.ForeignKey(
        Bandeira,
        on_delete=models.CASCADE,
        related_name='aparelhos',
        verbose_name="Bandeira Tarifária"
    )
    data_cadastro = models.DateField(
        default=timezone.now,
        verbose_name="Data de Cadastro"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Aparelho"
        verbose_name_plural = "Aparelhos"
        ordering = ['-data_cadastro', 'ambiente', 'nome']
        indexes = [
            models.Index(fields=['data_cadastro']),
            models.Index(fields=['ambiente']),
            models.Index(fields=['estado']),
            models.Index(fields=['bandeira']),
        ]

    def __str__(self):
        return f"{self.nome} ({self.ambiente})"

    @property
    def consumo_diario_kwh(self):
        """Calcula o consumo diário em kWh"""
        return (self.potencia_watts * self.tempo_uso_diario_horas * self.quantidade) / Decimal('1000')

    @property
    def consumo_mensal_kwh(self):
        """Calcula o consumo mensal estimado em kWh"""
        return self.consumo_diario_kwh * Decimal('30')

    @property
    def custo_diario(self):
        """Calcula o custo diário com tarifa normal"""
        tarifa_total = self.estado.tarifa.valor_kwh + self.bandeira.valor_adicional
        return self.consumo_diario_kwh * tarifa_total

    @property
    def custo_mensal(self):
        """Calcula o custo mensal com tarifa normal"""
        return self.custo_diario * Decimal('30')

    @property
    def custo_social_diario(self):
        """Calcula o custo diário com tarifa social"""
        tarifa_social = self.calcular_tarifa_social()
        return self.consumo_diario_kwh * tarifa_social

    @property
    def custo_social_mensal(self):
        """Calcula o custo mensal com tarifa social"""
        return self.custo_social_diario * Decimal('30')

    def calcular_tarifa_social(self):
        """Determina a tarifa social baseada no consumo mensal"""
        consumo_mensal = self.consumo_mensal_kwh

        try:
            if consumo_mensal <= Decimal('30'):
                desconto = Decimal('0.65')
            elif consumo_mensal <= Decimal('100'):
                desconto = Decimal('0.40')
            elif consumo_mensal <= Decimal('220'):
                desconto = Decimal('0.10')
            else:
                desconto = Decimal('0')

            # Usa a tarifa base do estado como referência
            tarifa_base = self.estado.tarifa.valor_kwh
            return tarifa_base * (Decimal('1') - desconto)
        except Exception:
            # Fallback em caso de erro
            return Decimal('0.50')


class HistoricoConsumo(models.Model):
    """Armazena o histórico de consumo por ambiente e data"""
    data = models.DateField(verbose_name="Data")
    ambiente = models.ForeignKey(
        Ambiente,
        on_delete=models.CASCADE,
        related_name='historico',
        verbose_name="Ambiente"
    )
    consumo_kwh = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Consumo (kWh)"
    )
    custo_normal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Custo Normal (R$)"
    )
    custo_social = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Custo Social (R$)"
    )
    aparelhos = models.ManyToManyField(
        Aparelho,
        related_name='historico',
        verbose_name="Aparelhos"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Histórico de Consumo"
        verbose_name_plural = "Históricos de Consumo"
        ordering = ['-data', 'ambiente']
        unique_together = ('data', 'ambiente')
        indexes = [
            models.Index(fields=['-data']),
            models.Index(fields=['ambiente']),
        ]

    def __str__(self):
        return f"{self.data.strftime('%d/%m/%Y')} - {self.ambiente}"

    @classmethod
    def atualizar_historico(cls, ambiente, data):
        """Atualiza ou cria um registro no histórico para um ambiente e data"""
        aparelhos = Aparelho.objects.filter(ambiente=ambiente, data_cadastro=data)

        if aparelhos.exists():
            consumo_total = sum(a.consumo_diario_kwh for a in aparelhos)
            custo_normal = sum(a.custo_diario for a in aparelhos)
            custo_social = sum(a.custo_social_diario for a in aparelhos)

            historico, created = cls.objects.update_or_create(
                data=data,
                ambiente=ambiente,
                defaults={
                    'consumo_kwh': consumo_total,
                    'custo_normal': custo_normal,
                    'custo_social': custo_social
                }
            )

            # Atualiza a relação many-to-many com os aparelhos
            historico.aparelhos.set(aparelhos)
            return historico
        else:
            # Remove o histórico se não houver aparelhos
            cls.objects.filter(data=data, ambiente=ambiente).delete()
            return None

#--------------Geral------------#
class ConfiguracaoSistema(models.Model):
    """Armazena configurações gerais do sistema"""
    chave = models.CharField(max_length=50, unique=True)
    valor = models.TextField()
    descricao = models.TextField(blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuração do Sistema"
        verbose_name_plural = "Configurações do Sistema"

    def __str__(self):
        return self.chave

    @classmethod
    def get_config(cls, chave, padrao=None):
        try:
            return cls.objects.get(chave=chave).valor
        except cls.DoesNotExist:
            return padrao

#-----------------Medidor------------------#

class ConsumoMensal(models.Model):
    ano = models.PositiveIntegerField()
    mes = models.PositiveIntegerField()  # 1 a 12

    estado = models.ForeignKey('Estado', on_delete=models.PROTECT)
    bandeira = models.ForeignKey('Bandeira', on_delete=models.PROTECT)
    tarifa_social = models.BooleanField(default=False)

    leitura_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    leitura_final = models.DecimalField(max_digits=10, decimal_places=2)

    consumo_kwh = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_pagar = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('ano', 'mes', 'estado', 'bandeira')
        ordering = ['-ano', '-mes']

    def calcular_consumo(self):
        if self.leitura_final and self.leitura_inicial:
            consumo = self.leitura_final - self.leitura_inicial
            if consumo < 0:
                consumo = Decimal('0')
            return consumo
        return Decimal('0')

    def obter_desconto_tarifa_social(self, consumo):
        faixa = None
        try:
            if consumo <= 30:
                faixa = 'ate_30'
            elif consumo <= 100:
                faixa = '31_a_100'
            elif consumo <= 220:
                faixa = '101_a_220'
            else:
                faixa = 'acima_220'
            tarifa_social_obj = TarifaSocial.objects.get(faixa_consumo=faixa)
            desconto_pct = tarifa_social_obj.desconto_percentual / Decimal('100')
            return desconto_pct
        except TarifaSocial.DoesNotExist:
            return Decimal('0')

    def save(self, *args, **kwargs):
        self.consumo_kwh = self.calcular_consumo()

        tarifa_base = self.estado.tarifa.valor_kwh
        adicional_bandeira = self.bandeira.valor_adicional
        tarifa_total = tarifa_base + adicional_bandeira

        custo_normal = self.consumo_kwh * tarifa_total

        if self.tarifa_social:
            desconto_pct = self.obter_desconto_tarifa_social(self.consumo_kwh)
            custo_com_desconto = custo_normal * (Decimal('1') - desconto_pct)
            self.total_pagar = custo_com_desconto.quantize(Decimal('0.01'))
        else:
            self.total_pagar = custo_normal.quantize(Decimal('0.01'))

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Consumo {self.mes:02d}/{self.ano} - {self.estado.nome} - {self.bandeira.get_cor_display()}"

#--------------OCR-----------#

class LeituraOCR(models.Model):
    valor_extraido = models.DecimalField(max_digits=10, decimal_places=2)
    valor_corrigido = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)
    bandeira = models.ForeignKey(Bandeira, on_delete=models.PROTECT)
    tarifa_social = models.BooleanField(default=False)
    data_registro = models.DateTimeField(auto_now_add=True)
    imagem = models.ImageField(upload_to='leituras_imagens/')

    consumo_entre_leituras = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def custo_total(self):
        if self.consumo_entre_leituras is None:
            return None

        tarifa = float(self.estado.tarifa.valor_kwh)
        adicional = float(self.bandeira.valor_adicional)
        consumo = float(self.consumo_entre_leituras)

        custo_bruto = consumo * (tarifa + adicional)

        if not self.tarifa_social:
            return round(custo_bruto, 2)

        desconto = self._obter_desconto_tarifa_social(consumo)

        custo_liquido = custo_bruto * (1 - desconto / 100)

        return round(custo_liquido, 2)

    def _obter_desconto_tarifa_social(self, consumo_kwh: float) -> float:
        """Busca a faixa correta da tarifa social baseada no consumo."""

        faixa = None
        if consumo_kwh <= 30:
            faixa = 'ate_30'
        elif 31 <= consumo_kwh <= 100:
            faixa = '31_a_100'
        elif 101 <= consumo_kwh <= 220:
            faixa = '101_a_220'
        else:
            faixa = 'acima_220'

        try:
            tarifa_social_obj = TarifaSocial.objects.get(faixa_consumo=faixa)
            return float(tarifa_social_obj.desconto_percentual)
        except TarifaSocial.DoesNotExist:
            return 0.0

    def __str__(self):
        return f"Leitura {self.valor_corrigido} kWh em {self.data_registro.date()}"