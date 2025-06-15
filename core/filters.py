import django_filters
from .models import LeituraOCR, Aparelho, ConsumoMensal, Estado, Bandeira


class LeituraOCRFilter(django_filters.FilterSet):
    mes = django_filters.NumberFilter(field_name='data_registro', lookup_expr='month')
    ano = django_filters.NumberFilter(field_name='data_registro', lookup_expr='year')

    class Meta:
        model = LeituraOCR
        fields = ['mes', 'ano']


class AparelhoFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(field_name='nome', lookup_expr='icontains')

    class Meta:
        model = Aparelho
        fields = {
            'ambiente': ['exact'],
            'estado': ['exact'],
            'data_cadastro': ['gte'],
        }


class ConsumoMensalFilter(django_filters.FilterSet):
    dia = django_filters.NumberFilter(field_name='criado_em', lookup_expr='day')

    class Meta:
        model = ConsumoMensal
        fields = ['estado', 'bandeira', 'ano', 'mes', 'dia']