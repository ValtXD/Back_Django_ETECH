from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
#Esse core pode tá vermehlo, mas tá dando certo (pra mim)
#Caso dê erro, verifique -> energy_manager.core.views (Depende do Interpretador)
from core.views import AmbienteViewSet, EstadoViewSet, BandeiraViewSet, AparelhoViewSet, CalculoConsumoAPIView, ResultadosAPIView, monitoramento_api, dicas_economia, resultados_contador, grafico_contador, LeituraOCRViewSet, OCRView, grafico_contador_anual, ConsumoMensalViewSet, OCRGeminiView, RegisterView, ProcessarDocumentoAPIView, CalcularCustosDocumentoAPIView, baixar_template, AiTipListCreateView, AiTipDetailView, ApplianceAiTipListCreateView, ApplianceAiTipDetailView
#from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Definindo as rotas dos ViewSets com o DefaultRouter
router = DefaultRouter()
router.register(r'ambientes', AmbienteViewSet)
router.register(r'estados', EstadoViewSet)
router.register(r'bandeiras', BandeiraViewSet)
router.register(r'aparelhos', AparelhoViewSet)
router.register(r'consumo-mensal', ConsumoMensalViewSet)
router.register(r'leituras-ocr', LeituraOCRViewSet)

urlpatterns = [
    # Admin do Django
    path('admin/', admin.site.urls),

    # Roteamento das APIs com o Router (ambientes, estados, etc.)
    path('api/', include(router.urls)),

    # APIs específicas de aparelhos e consumo
    path('api/calcular/', CalculoConsumoAPIView.as_view(), name='calcular-consumo'),
    path('api/resultados/', ResultadosAPIView.as_view(), name='resultados'),
    path('api/dicas-economia/', dicas_economia, name='dicas-economia'),

    # API para monitoramento (geral, não específica para contador)
    path('api/monitoramento/', monitoramento_api, name='monitoramento_api'),

    # API para consumo mensal
    #path('api/consumo-mensal/', consumo_mensal_view, name='consumo_mensal'),

    # API para resultados e gráfico do contador
    path('api/resultados-contador/', resultados_contador, name='resultados_contador'),
    path('api/grafico-contador/', grafico_contador, name='grafico_contador'),
    path('api/grafico-contador-anual/', grafico_contador_anual, name='grafico-contador-anual'),

    # API para deletar um consumo mensal específico (não precisa)
    #path('api/deletar-consumo-mensal/<int:pk>/', deletar_consumo_mensal, name='deletar_registro_contador'),

    #API para OCR -> TesseractOCR (Baixar)
    path('ocr/', OCRView.as_view(), name='ocr'),

    # Rota para o OCR usando Gemini IA
    path('ocr-gemini/', OCRGeminiView.as_view(), name='ocr-gemini'),

    #API para Login_Cadastro
    #path('register/', RegisterView.as_view(), name='register'),
    #path('login/', CustomTokenView.as_view(), name='token_obtain_pair'),
    #path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    #API para Login_Cadastro_Django - ERRO
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    #API para Leitura_Documento
    path('api/processar-documento/', ProcessarDocumentoAPIView.as_view(), name='processar-documento'),
    path('api/calcular-custos/', CalcularCustosDocumentoAPIView.as_view(), name='calcular-custos'),

    #API para Execel e Word (Leitura_Documento) -> Baixar Template
    path('baixar-template/<str:tipo>/<str:formato>/', baixar_template, name='baixar_template'),

    #API para Registrar IA Contador
    path('api/ai-tips/', AiTipListCreateView.as_view(), name='ai-tip-list-create'),
    path('api/ai-tips/<int:pk>/', AiTipDetailView.as_view(), name='ai-tip-detail'),

    #API para Registrar IA Aparelhos
    path('api/appliance-ai-tips/', ApplianceAiTipListCreateView.as_view(), name='appliance-ai-tip-list-create'),
    path('api/appliance-ai-tips/<int:pk>/', ApplianceAiTipDetailView.as_view(), name='appliance-ai-tip-detail'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)