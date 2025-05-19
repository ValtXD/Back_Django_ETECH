# core/serializers.py
from rest_framework import serializers
from .models import Ambiente, Estado, Bandeira, Aparelho, HistoricoConsumo, ContadorEnergia


class AmbienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ambiente
        fields = '__all__'


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = '__all__'


class BandeiraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bandeira
        fields = '__all__'

#-----------Aparelho------------#


class AparelhoSerializer(serializers.ModelSerializer):
    ambiente = AmbienteSerializer(read_only=True)
    estado = EstadoSerializer(read_only=True)
    bandeira = BandeiraSerializer(read_only=True)

    ambiente_id = serializers.PrimaryKeyRelatedField(
        source='ambiente', queryset=Ambiente.objects.all(), write_only=True
    )
    estado_id = serializers.PrimaryKeyRelatedField(
        source='estado', queryset=Estado.objects.all(), write_only=True
    )
    bandeira_id = serializers.PrimaryKeyRelatedField(
        source='bandeira', queryset=Bandeira.objects.all(), write_only=True
    )

    consumo_diario_kwh = serializers.ReadOnlyField()
    consumo_mensal_kwh = serializers.ReadOnlyField()
    custo_diario = serializers.ReadOnlyField()
    custo_mensal = serializers.ReadOnlyField()
    custo_social_diario = serializers.ReadOnlyField()
    custo_social_mensal = serializers.ReadOnlyField()

    class Meta:
        model = Aparelho
        fields = '__all__'



class HistoricoConsumoSerializer(serializers.ModelSerializer):
    ambiente = serializers.StringRelatedField()

    class Meta:
        model = HistoricoConsumo
        fields = [
            'id',
            'data',
            'ambiente',
            'consumo_kwh',
            'custo_normal',
            'custo_social',
            'criado_em',
            'atualizado_em'
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em']

#-----------Medidor------------#

class ContadorEnergiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContadorEnergia
        fields = '__all__'