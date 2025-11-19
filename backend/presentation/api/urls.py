from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import CabinaViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'cabinas', CabinaViewSet, basename='cabina')

urlpatterns = [
    # Auth
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Cabinas
    path('', include(router.urls)),
]

