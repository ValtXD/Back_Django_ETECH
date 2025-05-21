from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Ambiente, Estado, Tarifa, Bandeira,
    TarifaSocial, Aparelho, HistoricoConsumo,
    ConfiguracaoSistema, ConsumoMensal, LeituraOCR
)

class AmbienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao_curta', 'qtd_aparelhos', 'criado_em')
    search_fields = ('nome', 'descricao')
    list_filter = ('criado_em',)
    ordering = ('nome',)

    def descricao_curta(self, obj):
        return obj.descricao[:50] + '...' if obj.descricao else '-'

    descricao_curta.short_description = 'Descrição'

    def qtd_aparelhos(self, obj):
        return obj.aparelhos.count()

    qtd_aparelhos.short_description = 'Aparelhos'


class EstadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla', 'tarifa_atual')
    search_fields = ('nome', 'sigla')
    ordering = ('nome',)

    def tarifa_atual(self, obj):
        if hasattr(obj, 'tarifa'):
            return f"R$ {obj.tarifa.valor_kwh:.5f}/kWh"
        return '-'

    tarifa_atual.short_description = 'Tarifa'


class TarifaAdmin(admin.ModelAdmin):
    list_display = ('estado', 'valor_kwh_formatado', 'atualizado_em')
    search_fields = ('estado__nome', 'estado__sigla')
    list_filter = ('atualizado_em',)
    ordering = ('estado__nome',)

    def valor_kwh_formatado(self, obj):
        return f"R$ {obj.valor_kwh:.5f}/kWh"

    valor_kwh_formatado.short_description = 'Valor kWh'


class BandeiraAdmin(admin.ModelAdmin):
    list_display = ('cor_formatada', 'valor_adicional_formatado', 'descricao_curta')
    list_filter = ['cor']
    search_fields = ['cor', 'descricao']
    ordering = ['cor']

    def cor_formatada(self, obj):
        colors = {
            'verde': 'green',
            'amarela': 'orange',
            'vermelha1': 'crimson',
            'vermelha2': 'darkred'
        }
        color = colors.get(obj.cor, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_cor_display()
        )
    cor_formatada.short_description = 'Bandeira'

    def valor_adicional_formatado(self, obj):
        return f"R$ {obj.valor_adicional:.5f}/kWh"
    valor_adicional_formatado.short_description = 'Adicional'

    def descricao_curta(self, obj):
        return obj.descricao[:80] + '...' if len(obj.descricao) > 80 else obj.descricao
    descricao_curta.short_description = 'Descrição'

class TarifaSocialAdmin(admin.ModelAdmin):
    list_display = ('faixa_consumo_formatada', 'desconto_formatado', 'descricao_curta')
    ordering = ('desconto_percentual',)

    def faixa_consumo_formatada(self, obj):
        return obj.get_faixa_consumo_display()

    faixa_consumo_formatada.short_description = 'Faixa de Consumo'

    def desconto_formatado(self, obj):
        return f"{obj.desconto_percentual}%"

    desconto_formatado.short_description = 'Desconto'

    def descricao_curta(self, obj):
        return obj.descricao[:100] + '...' if obj.descricao else '-'

    descricao_curta.short_description = 'Descrição'

#------------Aparelho----------#
class AparelhoAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 'ambiente', 'potencia_formatada',
        'horas_uso', 'quantidade', 'consumo_diario_formatado',
        'custo_diario_formatado', 'data_cadastro'
    )
    list_filter = (
        'ambiente', 'estado', 'bandeira',
        'data_cadastro', 'criado_em'
    )
    search_fields = ('nome', 'ambiente__nome')
    ordering = ('-data_cadastro', 'ambiente')
    date_hierarchy = 'data_cadastro'
    readonly_fields = ('criado_em', 'atualizado_em')
    fieldsets = (
        (None, {
            'fields': ('nome', 'ambiente', 'data_cadastro')
        }),
        ('Consumo', {
            'fields': (
                'potencia_watts',
                'tempo_uso_diario_horas',
                'quantidade'
            )
        }),
        ('Tarifas', {
            'fields': ('estado', 'bandeira')
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )

    def potencia_formatada(self, obj):
        return f"{obj.potencia_watts} W"

    potencia_formatada.short_description = 'Potência'

    def horas_uso(self, obj):
        return f"{obj.tempo_uso_diario_horas} h/dia"

    horas_uso.short_description = 'Uso Diário'

    def consumo_diario_formatado(self, obj):
        return f"{obj.consumo_diario_kwh:.3f} kWh"

    consumo_diario_formatado.short_description = 'Consumo/Dia'

    def custo_diario_formatado(self, obj):
        return f"R$ {obj.custo_diario:.2f}"

    custo_diario_formatado.short_description = 'Custo/Dia'


class HistoricoConsumoAdmin(admin.ModelAdmin):
    list_display = (
        'data', 'ambiente', 'consumo_formatado',
        'custo_normal_formatado', 'custo_social_formatado',
        'qtd_aparelhos'
    )
    list_filter = ('data', 'ambiente')
    search_fields = ('ambiente__nome',)
    date_hierarchy = 'data'
    readonly_fields = ('criado_em', 'atualizado_em')

    def consumo_formatado(self, obj):
        return f"{obj.consumo_kwh:.2f} kWh"

    consumo_formatado.short_description = 'Consumo'

    def custo_normal_formatado(self, obj):
        return f"R$ {obj.custo_normal:.2f}"

    custo_normal_formatado.short_description = 'Custo Normal'

    def custo_social_formatado(self, obj):
        return f"R$ {obj.custo_social:.2f}"

    custo_social_formatado.short_description = 'Custo Social'

    def qtd_aparelhos(self, obj):
        return obj.aparelhos.count()

    qtd_aparelhos.short_description = 'Aparelhos'


class ConfiguracaoSistemaAdmin(admin.ModelAdmin):
    list_display = ('chave', 'valor_curto', 'atualizado_em')
    search_fields = ('chave', 'descricao')
    readonly_fields = ('atualizado_em',)

    def valor_curto(self, obj):
        return obj.valor[:100] + ('...' if len(obj.valor) > 100 else '')

    valor_curto.short_description = 'Valor'

    def has_add_permission(self, request):
        # Impede a adição de novas configurações via admin
        return False


# Registro dos modelos
admin.site.register(Ambiente, AmbienteAdmin)
admin.site.register(Estado, EstadoAdmin)
admin.site.register(Tarifa, TarifaAdmin)
admin.site.register(Bandeira, BandeiraAdmin)
admin.site.register(TarifaSocial, TarifaSocialAdmin)
admin.site.register(Aparelho, AparelhoAdmin)
admin.site.register(HistoricoConsumo, HistoricoConsumoAdmin)
admin.site.register(ConfiguracaoSistema, ConfiguracaoSistemaAdmin)

# Personalização do Admin
admin.site.site_header = "Energy Manager - Administração"
admin.site.site_title = "Sistema de Gerenciamento de Energia"
admin.site.index_title = "Painel de Controle"

#----------------Medidor---------------#

@admin.register(ConsumoMensal)
class ConsumoMensalAdmin(admin.ModelAdmin):
    list_display = ('ano', 'mes', 'estado', 'bandeira', 'tarifa_social', 'consumo_kwh', 'total_pagar')
    list_filter = ('ano', 'mes', 'estado', 'bandeira', 'tarifa_social')
    search_fields = ('estado__nome', 'bandeira__cor')
    ordering = ('-ano', '-mes')
    date_hierarchy = 'criado_em'  # Se quiser hierarquia por data de criação

#--------------OCR-----------#

@admin.register(LeituraOCR)
class LeituraOCRAdmin(admin.ModelAdmin):
    list_display = (
        'data_registro', 'estado', 'bandeira',
        'valor_extraido', 'valor_corrigido',
        'consumo_entre_leituras', 'tarifa_social', 'get_custo_total', 'imagem_preview'
    )
    list_filter = ('estado', 'bandeira', 'tarifa_social', 'data_registro')
    search_fields = ('estado__nome', 'bandeira__cor')
    ordering = ('-data_registro',)
    readonly_fields = ('data_registro', 'consumo_entre_leituras', 'get_custo_total', 'imagem_preview')

    def get_custo_total(self, obj):
        custo = obj.custo_total()
        if custo is None:
            return '-'
        return f"R$ {custo:.2f}"
    get_custo_total.short_description = 'Custo Estimado'

    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" width="100" />', obj.imagem.url)
        return '-'
    imagem_preview.short_description = 'Imagem'

    def has_add_permission(self, request):
        # Bloqueia criação manual pelo admin para evitar inconsistência
        return False

    def has_change_permission(self, request, obj=None):
        # Permite edição se desejar, ou deixe False para só leitura
        return True

    def has_delete_permission(self, request, obj=None):
        return True

