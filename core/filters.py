import django_filters
from .models import LeituraOCR

class LeituraOCRFilter(django_filters.FilterSet):
    mes = django_filters.NumberFilter(field_name='data_registro', lookup_expr='month')
    ano = django_filters.NumberFilter(field_name='data_registro', lookup_expr='year')

    class Meta:
        model = LeituraOCR
        fields = ['mes', 'ano']
