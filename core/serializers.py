# core/serializers.py
from rest_framework import serializers
from .models import Ambiente, Estado, Bandeira, Aparelho, HistoricoConsumo, ConsumoMensal, LeituraOCR, Tarifa
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from decimal import Decimal, InvalidOperation

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


#class TarifaSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Tarifa
#        fields = ['valor_kwh']

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

class ConsumoMensalSerializer(serializers.ModelSerializer):
    estado_nome = serializers.CharField(source='estado.nome', read_only=True)
    bandeira_cor = serializers.CharField(source='bandeira.cor', read_only=True)

    class Meta:
        model = ConsumoMensal
        fields = [
            'id', 'ano', 'mes', 'estado', 'estado_nome',
            'bandeira', 'bandeira_cor', 'tarifa_social',
            'leitura_inicial', 'leitura_final', 'consumo_kwh',
            'total_pagar', 'criado_em', 'atualizado_em'
        ]

#--------------OCR-----------#

class LeituraOCRSerializer(serializers.ModelSerializer):
    estado = EstadoSerializer(read_only=True)
    bandeira = BandeiraSerializer(read_only=True)
    estado_id = serializers.PrimaryKeyRelatedField(queryset=Estado.objects.all(), source='estado', write_only=True)
    bandeira_id = serializers.PrimaryKeyRelatedField(queryset=Bandeira.objects.all(), source='bandeira', write_only=True)
    imagem_url = serializers.SerializerMethodField()
    tarifa_social = serializers.BooleanField()
    custo_total = serializers.SerializerMethodField()
    consumo_entre_leituras = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    tarifa_valor_kwh = serializers.SerializerMethodField()

    class Meta:
        model = LeituraOCR
        fields = [
            'id', 'valor_extraido', 'valor_corrigido', 'estado', 'bandeira',
            'tarifa_social', 'data_registro', 'estado_id', 'bandeira_id',
            'imagem', 'imagem_url', 'consumo_entre_leituras', 'custo_total', 'tarifa_valor_kwh',
        ]
        extra_kwargs = {'imagem': {'write_only': True}}

    def get_tarifa_valor_kwh(self, obj):
        return obj.estado.tarifa.valor_kwh if obj.estado and hasattr(obj.estado, 'tarifa') else None

    def get_imagem_url(self, obj):
        request = self.context.get('request')
        if obj.imagem and request:
            return request.build_absolute_uri(obj.imagem.url)
        return None

    def get_custo_total(self, obj):
        if hasattr(obj, 'custo_total') and callable(obj.custo_total):
            return obj.custo_total()
        return None

    def create(self, validated_data):
        leitura = LeituraOCR.objects.create(**validated_data)

        leituras_anteriores = LeituraOCR.objects.filter(
            estado=leitura.estado,
            data_registro__lt=leitura.data_registro
        ).order_by('-data_registro')

        if leituras_anteriores.exists():
            ultima = leituras_anteriores.first()
            consumo = leitura.valor_corrigido - ultima.valor_corrigido
            leitura.consumo_entre_leituras = consumo if consumo >= 0 else None
        else:
            leitura.consumo_entre_leituras = None

        leitura.save()
        return leitura

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        leituras_anteriores = LeituraOCR.objects.filter(
            estado=instance.estado,
            data_registro__lt=instance.data_registro
        ).order_by('-data_registro')

        if leituras_anteriores.exists():
            ultima = leituras_anteriores.first()
            consumo = instance.valor_corrigido - ultima.valor_corrigido
            instance.consumo_entre_leituras = consumo if consumo >= 0 else None
        else:
            instance.consumo_entre_leituras = None

        instance.save()
        return instance

#-------------Gemini------------------#

    def validate_valor_extraido(self, value):
        try:
            val = Decimal(value)
            if val < 0:
                raise serializers.ValidationError("Valor extraído deve ser positivo.")
            return val
        except InvalidOperation:
            raise serializers.ValidationError("Valor extraído inválido.")

    def validate_valor_corrigido(self, value):
        try:
            val = Decimal(value)
            if val < 0:
                raise serializers.ValidationError("Valor corrigido deve ser positivo.")
            return val
        except InvalidOperation:
            raise serializers.ValidationError("Valor corrigido inválido.")

#    def get_tarifa_valor_kwh(self, obj):
#        try:
#            return obj.tarifa.valor_kwh
#        except Tarifa.DoesNotExist:
#            return None

#---------------Login-Cadastro--------------------#

#User = get_user_model()

#class RegisterSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = User
#        fields = ('id', 'username', 'password', 'email')
#        extra_kwargs = {'password': {'write_only': True}}
#
#    def create(self, validated_data):
#        return User.objects.create_user(**validated_data)

#class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#    @classmethod
#    def get_token(cls, user):
#        token = super().get_token(user)
#        token['username'] = user.username
#        return token