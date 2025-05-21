from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
#Esse core pode tá vermehlo, mas tá dando certo
#Caso de erro, verifique -> energy_manager.core.views
from core.views import AmbienteViewSet, EstadoViewSet, BandeiraViewSet, AparelhoViewSet, CalculoConsumoAPIView, ResultadosAPIView, monitoramento_api, dicas_economia, consumo_mensal_view, resultados_contador, grafico_contador, deletar_consumo_mensal, LeituraOCRViewSet, OCRView
from django.conf import settings
from django.conf.urls.static import static

# Definindo as rotas dos ViewSets com o DefaultRouter
router = DefaultRouter()
router.register(r'ambientes', AmbienteViewSet)
router.register(r'estados', EstadoViewSet)
router.register(r'bandeiras', BandeiraViewSet)
router.register(r'aparelhos', AparelhoViewSet)
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
    path('api/consumo-mensal/', consumo_mensal_view, name='consumo_mensal'),

    # API para resultados e gráfico do contador
    path('api/resultados-contador/', resultados_contador, name='resultados_contador'),
    path('api/grafico-contador/', grafico_contador, name='grafico_contador'),

    # API para deletar um consumo mensal específico
    path('api/deletar-consumo-mensal/<int:pk>/', deletar_consumo_mensal, name='deletar_registro_contador'),

    #API para OCR -> TesseractOCR (Baixar)
    path('ocr/', OCRView.as_view(), name='ocr'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)