from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.views import APIView
import json
from django.http import JsonResponse
from .models import Ambiente, Aparelho, HistoricoConsumo, Estado, Bandeira, TarifaSocial, ContadorEnergia
from django.db.models import Sum
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from .serializers import (
    AmbienteSerializer, EstadoSerializer,
    BandeiraSerializer, AparelhoSerializer,
    HistoricoConsumoSerializer, ContadorEnergiaSerializer
)
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import google.generativeai as genai
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
import json

# Configuração da API Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

# Views baseadas em classes para a API
class AmbienteViewSet(viewsets.ModelViewSet):
    queryset = Ambiente.objects.all()
    serializer_class = AmbienteSerializer


class EstadoViewSet(viewsets.ModelViewSet):
    queryset = Estado.objects.all().select_related('tarifa')
    serializer_class = EstadoSerializer


class BandeiraViewSet(viewsets.ModelViewSet):
    queryset = Bandeira.objects.all()
    serializer_class = BandeiraSerializer


class AparelhoViewSet(viewsets.ModelViewSet):
    queryset = Aparelho.objects.all().select_related('ambiente', 'estado', 'bandeira')
    serializer_class = AparelhoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        data = self.request.query_params.get('data')

        if data:
            try:
                data_obj = datetime.strptime(data, '%Y-%m-%d').date()
                queryset = queryset.filter(data_cadastro=data_obj)
            except ValueError:
                pass
        return queryset


class HistoricoConsumoViewSet(viewsets.ModelViewSet):
    queryset = HistoricoConsumo.objects.all().select_related('ambiente')
    serializer_class = HistoricoConsumoSerializer
    filterset_fields = ['data', 'ambiente']

#------------------Aparelho------------------#
class CalculoConsumoAPIView(APIView):
    def post(self, request):
        try:
            data = request.data
            potencia = Decimal(data.get('potencia_watts'))
            horas = Decimal(data.get('tempo_uso_diario_horas'))
            quantidade = int(data.get('quantidade', 1))

            # Cálculo do consumo em kWh
            consumo_diario = (potencia * horas * quantidade) / Decimal('1000')

            # Obter tarifas
            estado = Estado.objects.get(id=data.get('estado'))
            bandeira = Bandeira.objects.get(id=data.get('bandeira'))

            # Cálculo do custo normal
            tarifa_total = estado.tarifa.valor_kwh + bandeira.valor_adicional
            custo_normal = consumo_diario * tarifa_total

            # Cálculo do custo social
            consumo_mensal = consumo_diario * Decimal('30')
            tarifa_social = self.calcular_tarifa_social(consumo_mensal)
            custo_social = consumo_diario * tarifa_social

            response_data = {
                'consumo_diario_kwh': float(consumo_diario),
                'consumo_mensal_kwh': float(consumo_mensal),
                'custo_diario_normal': float(custo_normal),
                'custo_mensal_normal': float(custo_normal * Decimal('30')),
                'custo_diario_social': float(custo_social),
                'custo_mensal_social': float(custo_social * Decimal('30')),
                'tarifa_normal': float(tarifa_total),
                'tarifa_social': float(tarifa_social),
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def calcular_tarifa_social(self, consumo_mensal):
        """Calcula a tarifa social baseada no consumo mensal"""
        try:
            if consumo_mensal <= 30:
                desconto = Decimal('0.65')
            elif consumo_mensal <= 100:
                desconto = Decimal('0.40')
            elif consumo_mensal <= 220:
                desconto = Decimal('0.10')
            else:
                desconto = Decimal('0')

            # Tarifa base do estado de São Paulo como referência
            tarifa_base = Decimal('0.67123')
            return tarifa_base * (Decimal('1') - desconto)
        except Exception:
            return Decimal('0.50')  # Fallback


class ResultadosAPIView(generics.ListAPIView):
    serializer_class = AparelhoSerializer

    def get_queryset(self):
        # Obter todas as datas distintas com aparelhos cadastrados
        datas_disponiveis = Aparelho.objects.dates('data_cadastro', 'day').order_by('-data_cadastro')

        # Data selecionada (padrão: mais recente)
        data_selecionada = self.request.query_params.get('data')
        if not data_selecionada and datas_disponiveis:
            data_selecionada = datas_disponiveis[0].strftime('%Y-%m-%d')

        # Processar aparelhos da data selecionada
        if data_selecionada:
            try:
                data_obj = datetime.strptime(data_selecionada, '%Y-%m-%d').date()
                return Aparelho.objects.filter(data_cadastro=data_obj).select_related('ambiente', 'estado', 'bandeira')
            except ValueError:
                return Aparelho.objects.none()
        return Aparelho.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Calcular totais
        consumo_total_dia = sum(a.consumo_diario_kwh for a in queryset)
        custo_total_normal = sum(a.custo_diario for a in queryset)
        custo_total_social = sum(a.custo_social_diario for a in queryset)

        # Obter datas disponíveis para o filtro
        datas_disponiveis = Aparelho.objects.dates('data_cadastro', 'day').order_by('-data_cadastro')

        response_data = {
            'data_selecionada': request.query_params.get('data'),
            'aparelhos': serializer.data,
            'consumo_total_dia': float(consumo_total_dia),
            'custo_total_normal': float(custo_total_normal),
            'custo_total_social': float(custo_total_social),
            'datas_disponiveis': [d.strftime('%Y-%m-%d') for d in datas_disponiveis],
        }

        return Response(response_data)


@method_decorator(csrf_exempt, name='dispatch')
class DicasEconomiaAPIView(generics.GenericAPIView):
    def post(self, request):
        try:
            dados = request.data

            model = genai.GenerativeModel('gemini-pro')

            prompt = f"""
            Analise estes dados de consumo de energia:
            {json.dumps(dados, indent=2)}

            Forneça 3 a 5 recomendações PRÁTICAS para economizar energia, com:
            - Foco nos maiores consumidores
            - Estimativas de economia potencial
            - Sugestões por ambiente
            - Formato: Lista numerada em português claro
            """

            response = model.generate_content(prompt)

            if not response.text:
                raise ValueError("Resposta vazia da API Gemini")

            return Response({
                'dicas': response.text,
                'status': 'success'
            })

        except json.JSONDecodeError:
            return Response({'error': 'JSON inválido'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"Erro na API: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Views baseadas em funções para compatibilidade com o frontend existente
def home(request):
    return render(request, 'home.html')


def calcular_consumo(request):
    if request.method == 'POST':
        data_cadastro = request.POST.get('data_cadastro', timezone.now().date())
        bandeira_value = request.POST.get('bandeira')

        try:
            if bandeira_value.isdigit():
                bandeira = Bandeira.objects.get(id=int(bandeira_value))
            else:
                bandeira = Bandeira.objects.get(cor=bandeira_value)

            estado = Estado.objects.get(id=int(request.POST.get('estado')))

            aparelho = Aparelho.objects.create(
                nome=request.POST.get('nome'),
                potencia_watts=float(request.POST.get('potencia')),
                tempo_uso_diario_horas=float(request.POST.get('horas')),
                quantidade=int(request.POST.get('quantidade')),
                ambiente_id=int(request.POST.get('ambiente')),
                estado=estado,
                bandeira=bandeira,
                data_cadastro=data_cadastro
            )

            return redirect('core:resultados')

        except Bandeira.DoesNotExist:
            return JsonResponse({'error': "Bandeira selecionada não encontrada."}, status=400)
        except Estado.DoesNotExist:
            return JsonResponse({'error': "Estado selecionado não encontrado."}, status=400)
        except Exception as e:
            return JsonResponse({'error': f"Erro ao salvar: {str(e)}"}, status=400)

    ambientes = Ambiente.objects.all()
    estados = Estado.objects.filter(tarifa__isnull=False).select_related('tarifa')
    bandeiras = Bandeira.objects.all()
    aparelhos = Aparelho.objects.all().order_by('-data_cadastro')

    return render(request, 'calcular.html', {
        'ambientes': ambientes,
        'estados': estados,
        'bandeiras': bandeiras,
        'aparelhos': aparelhos,
        'data_atual': timezone.now().date()
    })


def remover_aparelho(request, aparelho_id):
    aparelho = get_object_or_404(Aparelho, id=aparelho_id)
    data_cadastro = aparelho.data_cadastro
    ambiente = aparelho.ambiente
    aparelho.delete()

    atualizar_historico_consumo(ambiente, data_cadastro)

    if not Aparelho.objects.filter(data_cadastro=data_cadastro).exists():
        HistoricoConsumo.objects.filter(data=data_cadastro).delete()

    return redirect('core:calcular')


def resultados(request):
    datas_disponiveis = Aparelho.objects.dates('data_cadastro', 'day').order_by('-data_cadastro')

    data_selecionada = request.GET.get('data')
    if not data_selecionada and datas_disponiveis:
        data_selecionada = datas_disponiveis[0].strftime('%Y-%m-%d')

    if data_selecionada:
        try:
            data_obj = datetime.strptime(data_selecionada, '%Y-%m-%d').date()

            aparelhos_dia = Aparelho.objects.filter(
                data_cadastro=data_obj
            ).select_related('ambiente', 'estado', 'bandeira')

            consumo_total_dia = sum(a.consumo_diario_kwh for a in aparelhos_dia)
            custo_total_normal = sum(a.custo_diario for a in aparelhos_dia)
            custo_total_social = sum(a.custo_social_diario for a in aparelhos_dia)
        except ValueError:
            aparelhos_dia = []
            consumo_total_dia = 0
            custo_total_normal = 0
            custo_total_social = 0
    else:
        aparelhos_dia = []
        consumo_total_dia = 0
        custo_total_normal = 0
        custo_total_social = 0

    return render(request, 'resultados.html', {
        'data_selecionada': data_selecionada,
        'aparelhos_dia': aparelhos_dia,
        'consumo_total_dia': consumo_total_dia,
        'custo_total_normal': custo_total_normal,
        'custo_total_social': custo_total_social,
        'datas_disponiveis': datas_disponiveis,
    })

def atualizar_historico_consumo(ambiente, data):
    """Atualiza o histórico de consumo para um ambiente e data específicos"""
    from decimal import Decimal

    aparelhos = Aparelho.objects.filter(ambiente=ambiente, data_cadastro=data)
    consumo_total = float(sum(a.consumo_diario_kwh() for a in aparelhos))

    estado_padrao = Estado.objects.first()
    tarifa_normal = float(estado_padrao.tarifa.valor_kwh) if estado_padrao and estado_padrao.tarifa else 0.70

    tarifa_social = float(calcular_tarifa_social(consumo_total * 30))

    HistoricoConsumo.objects.update_or_create(
        data=data,
        ambiente=ambiente,
        defaults={
            'consumo_kwh': Decimal(str(consumo_total)),
            'custo_normal': Decimal(str(consumo_total * tarifa_normal)),
            'custo_social': Decimal(str(consumo_total * tarifa_social))
        }
    )


def calcular_tarifa_social(consumo_mensal):
    """Calcula a tarifa social baseada no consumo mensal"""
    try:
        if consumo_mensal <= 30:
            desconto = 0.65
        elif consumo_mensal <= 100:
            desconto = 0.40
        elif consumo_mensal <= 220:
            desconto = 0.10
        else:
            desconto = 0

        tarifa_base = 0.67123
        return tarifa_base * (1 - desconto)
    except Exception:
        return 0.50


@api_view(['GET'])
def monitoramento_api(request):
    """
    API para fornecer dados de monitoramento de consumo,
    retornando JSON para Angular consumir e montar gráfico.
    Aceita parâmetros:
      - periodo (YYYY-MM-DD)
      - modo (opcional, '30dias' para simular uso mensal)
    """
    periodo = request.GET.get('periodo')
    modo_30dias = request.GET.get('modo') == '30dias'

    if not periodo:
        return JsonResponse({'error': 'Parâmetro "periodo" é obrigatório.'}, status=400)

    try:
        data_obj = datetime.strptime(periodo, '%Y-%m-%d').date()

        # Sempre filtra apenas pelos aparelhos registrados na data selecionada
        aparelhos = Aparelho.objects.filter(data_cadastro=data_obj)

        ambientes = Ambiente.objects.all()

        dados = []
        for ambiente in ambientes:
            aparelhos_ambiente = aparelhos.filter(ambiente=ambiente)
            if aparelhos_ambiente.exists():
                consumo_total = sum(a.consumo_diario_kwh for a in aparelhos_ambiente)
                custo_normal = sum(a.custo_diario for a in aparelhos_ambiente)
                custo_social = sum(a.custo_social_diario for a in aparelhos_ambiente)

                dados.append({
                    'ambiente': ambiente.nome,
                    'consumo': float(consumo_total),
                    'custo_normal': float(custo_normal),
                    'custo_social': float(custo_social),
                    'aparelhos': list(set(a.nome for a in aparelhos_ambiente)),
                    'estados': list(set(a.estado.nome for a in aparelhos_ambiente)),
                    'bandeiras': list(set(a.bandeira.get_cor_display() for a in aparelhos_ambiente))
                })

        response = {
            'dados': dados,
            'periodo': periodo,
            'modo_30dias': modo_30dias,
        }

        return Response(response)

    except ValueError:
        return JsonResponse({'error': 'Formato de data inválido. Use YYYY-MM-DD.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)

@api_view(['POST'])
def dicas_economia(request):
    try:
        dados = request.data
        # Monte o prompt baseado nos dados recebidos
        prompt = f"""
        Dados de consumo recebidos: {json.dumps(dados, indent=2)}

        Forneça 3 a 5 dicas práticas para economizar energia, focando nos maiores consumidores e nos ambientes.
        """
        model = genai.GenerativeModel('gemini-pro')
        resposta = model.generate_content(prompt)

        if not resposta.text:
            return Response({'error': 'Resposta vazia da API Gemini'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'dicas': resposta.text})

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#---------Medidor----------#

@api_view(['GET', 'POST'])
def contador_energia_view(request):
    if request.method == 'POST':
        dados = request.data

        data_registro_str = dados.get('data_registro')
        if data_registro_str:
            try:
                data_registro = datetime.strptime(data_registro_str, '%Y-%m-%d')
            except ValueError:
                return Response({'error': 'Formato inválido para data_registro'}, status=400)
        else:
            data_registro = None

        leitura_anterior = Decimal(dados.get('leitura_anterior', 0))
        leitura_atual = Decimal(dados.get('leitura_atual', 0))

        if leitura_atual < leitura_anterior:
            return Response({'error': 'Leitura atual menor que a anterior'}, status=400)

        consumo = leitura_atual - leitura_anterior

        try:
            estado = Estado.objects.get(id=dados.get('estado'))
            bandeira = Bandeira.objects.get(id=dados.get('bandeira'))
        except (Estado.DoesNotExist, Bandeira.DoesNotExist):
            return Response({'error': 'Estado ou Bandeira inválidos'}, status=400)

        tarifa_base = estado.tarifa.valor_kwh  # valor_kwh do estado
        valor_adicional = bandeira.valor_adicional  # adicional da bandeira
        tarifa_total = tarifa_base + valor_adicional

        custo_normal = consumo * tarifa_total

        # Aqui você pode chamar sua função real para tarifa social ou manter fixo
        tarifa_social = Decimal('0.7')  # Exemplo fixo
        if dados.get('tarifa_social', False):
            custo_final = consumo * tarifa_social
        else:
            custo_final = custo_normal

        registro = ContadorEnergia.objects.create(
            estado=estado.nome,
            bandeira=bandeira.cor,
            tarifa_social=dados.get('tarifa_social', False),
            consumo_kwh=consumo,
            total_pagar=custo_final,
            data_registro=data_registro
        )

        serializer = ContadorEnergiaSerializer(registro)
        return Response(serializer.data, status=201)

    registros = ContadorEnergia.objects.all().order_by('-data_registro')
    serializer = ContadorEnergiaSerializer(registros, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def monitoramento_contador(request):
    registros = ContadorEnergia.objects.all()
    estados = [r.estado for r in registros]
    consumos = [float(r.consumo_kwh) for r in registros]
    totais = [float(r.total_pagar) for r in registros]
    return Response({'estados': estados, 'consumos': consumos, 'totais': totais})


@csrf_exempt
def deletar_registro_contador(request, pk):
    if request.method == 'POST':
        try:
            registro = ContadorEnergia.objects.get(pk=pk)
            registro.delete()
            return JsonResponse({'status': 'success'})
        except ContadorEnergia.DoesNotExist:
            return JsonResponse({'status': 'not_found'}, status=404)
    return JsonResponse({'status': 'invalid'}, status=400)