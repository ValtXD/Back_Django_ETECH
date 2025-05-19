# energy_manager/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import AmbienteViewSet, EstadoViewSet, BandeiraViewSet, AparelhoViewSet, CalculoConsumoAPIView, ResultadosAPIView, monitoramento_api, dicas_economia, contador_energia_view, monitoramento_contador, deletar_registro_contador
#from core import views

router = DefaultRouter()
router.register(r'ambientes', AmbienteViewSet)
router.register(r'estados', EstadoViewSet)
router.register(r'bandeiras', BandeiraViewSet)
router.register(r'aparelhos', AparelhoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    # APIs específicas de aparelhos
    path('api/calcular/', CalculoConsumoAPIView.as_view(), name='calcular-consumo'),
    path('api/resultados/', ResultadosAPIView.as_view(), name='resultados'),
    path('api/dicas-economia/', dicas_economia, name='dicas-economia'),

    # Pode ser view function ou class-based, depende de sua implementação
    path('api/monitoramento/', monitoramento_api, name='monitoramento_api'),

    #API de Medidor
    path('api/contador-energia/', contador_energia_view, name='contador_energia'),
    path('api/monitoramento-contador/', monitoramento_contador, name='monitoramento_contador'),
    #path('resultados-contador/', resultados_contador, name='resultados_contador'),
    path('deletar-registro-contador/<int:pk>/', deletar_registro_contador, name='deletar_registro_contador'),
]