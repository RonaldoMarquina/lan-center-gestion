from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'api'

urlpatterns = [
    # Autenticación JWT
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Aquí se agregarán las rutas de los endpoints de la API
    # path('cabinas/', include('presentation.api.cabinas.urls')),
    # path('usuarios/', include('presentation.api.usuarios.urls')),
    # path('reservas/', include('presentation.api.reservas.urls')),
]

