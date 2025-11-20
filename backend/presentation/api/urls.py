from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import CabinaViewSet, ReservaViewSet, SesionViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'cabinas', CabinaViewSet, basename='cabina')
router.register(r'reservas', ReservaViewSet, basename='reserva')
router.register(r'sesiones', SesionViewSet, basename='sesion')

urlpatterns = [
    # Auth
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Cabinas
    path('', include(router.urls)),
]

