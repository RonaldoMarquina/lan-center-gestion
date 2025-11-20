"""Tests de API para Reservas y Sesiones."""
import os
from datetime import datetime, timedelta
from decimal import Decimal

from django.test import override_settings
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

from infrastructure.persistence.models import CabinaModel, ReservaModel, SesionModel


# Override DB para usar SQLite in-memory en tests
@override_settings(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
)
class ReservaSesionApiTests(APITestCase):
    """Tests de endpoints de Reservas y Sesiones."""

    def setUp(self):
        """Crear usuario, JWT token y cabina de prueba."""
        self.user = User.objects.create_user(username='test', password='test123')
        
        # Obtener JWT token
        response = self.client.post('/api/auth/token/', {
            'username': 'test',
            'password': 'test123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Crear cabina de prueba
        self.cabina = CabinaModel.objects.create(
            numero=1,
            tipo='BASICA',
            estado='DISPONIBLE',
            especificaciones={},
            precio_por_hora=Decimal('5.00')
        )

    def test_crear_y_listar_reserva(self):
        """Crear una reserva y listarla."""
        inicio = datetime.now() + timedelta(hours=1)
        fin = inicio + timedelta(hours=2)
        
        response = self.client.post('/api/reservas/', {
            'usuario_id': self.user.id,
            'cabina_id': self.cabina.id,
            'fecha_hora_inicio': inicio.isoformat(),
            'fecha_hora_fin': fin.isoformat(),
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['estado'], 'pendiente')
        
        # Listar
        response = self.client.get('/api/reservas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_crear_reserva_con_conflicto(self):
        """Crear dos reservas con horarios conflictivos."""
        inicio1 = datetime.now() + timedelta(hours=1)
        fin1 = inicio1 + timedelta(hours=2)
        
        self.client.post('/api/reservas/', {
            'usuario_id': self.user.id,
            'cabina_id': self.cabina.id,
            'fecha_hora_inicio': inicio1.isoformat(),
            'fecha_hora_fin': fin1.isoformat(),
        })
        
        # Intentar crear otra que solape
        inicio2 = inicio1 + timedelta(minutes=30)
        fin2 = fin1 + timedelta(hours=1)
        
        response = self.client.post('/api/reservas/', {
            'usuario_id': self.user.id,
            'cabina_id': self.cabina.id,
            'fecha_hora_inicio': inicio2.isoformat(),
            'fecha_hora_fin': fin2.isoformat(),
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('conflicto', response.data['detail'].lower())

    def test_flujo_completo_reserva_a_sesion(self):
        """Flujo: crear reserva → confirmar → iniciar sesión → finalizar."""
        # 1. Crear reserva
        inicio = datetime.now() + timedelta(hours=1)
        fin = inicio + timedelta(hours=2)
        
        response = self.client.post('/api/reservas/', {
            'usuario_id': self.user.id,
            'cabina_id': self.cabina.id,
            'fecha_hora_inicio': inicio.isoformat(),
            'fecha_hora_fin': fin.isoformat(),
        })
        reserva_id = response.data['id']
        
        # 2. Confirmar reserva
        response = self.client.post(f'/api/reservas/{reserva_id}/confirmar/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['estado'], 'confirmada')
        
        # 3. Iniciar sesión
        response = self.client.post('/api/sesiones/', {
            'reserva_id': reserva_id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        sesion_id = response.data['id']
        self.assertEqual(response.data['estado'], 'activa')
        
        # Verificar que cabina está ocupada
        self.cabina.refresh_from_db()
        self.assertEqual(self.cabina.estado, 'OCUPADA')
        
        # 4. Finalizar sesión
        response = self.client.post(f'/api/sesiones/{sesion_id}/finalizar/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['estado'], 'finalizada')
        self.assertGreaterEqual(Decimal(response.data['costo_total']), Decimal('0'))
        
        # Verificar que cabina está disponible
        self.cabina.refresh_from_db()
        self.assertEqual(self.cabina.estado, 'DISPONIBLE')

    def test_cancelar_reserva(self):
        """Cancelar una reserva pendiente."""
        inicio = datetime.now() + timedelta(hours=1)
        fin = inicio + timedelta(hours=2)
        
        response = self.client.post('/api/reservas/', {
            'usuario_id': self.user.id,
            'cabina_id': self.cabina.id,
            'fecha_hora_inicio': inicio.isoformat(),
            'fecha_hora_fin': fin.isoformat(),
        })
        reserva_id = response.data['id']
        
        response = self.client.post(f'/api/reservas/{reserva_id}/cancelar/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['estado'], 'cancelada')

    def test_extender_sesion(self):
        """Extender una sesión activa."""
        # Crear y confirmar reserva
        inicio = datetime.now()
        fin = inicio + timedelta(hours=1)
        
        response = self.client.post('/api/reservas/', {
            'usuario_id': self.user.id,
            'cabina_id': self.cabina.id,
            'fecha_hora_inicio': inicio.isoformat(),
            'fecha_hora_fin': fin.isoformat(),
        })
        reserva_id = response.data['id']
        
        self.client.post(f'/api/reservas/{reserva_id}/confirmar/')
        
        # Iniciar sesión
        response = self.client.post('/api/sesiones/', {'reserva_id': reserva_id})
        sesion_id = response.data['id']
        tiempo_inicial = response.data['tiempo_total_minutos']
        
        # Extender
        response = self.client.post(f'/api/sesiones/{sesion_id}/extender/', {
            'minutos_adicionales': 30
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # No podemos verificar el tiempo porque la sesión activa no incrementa tiempo_total
        # hasta que se finaliza, pero se puede extender la duración permitida

    def test_listar_sesiones_activas(self):
        """Listar sesiones activas."""
        # Crear sesión activa
        inicio = datetime.now()
        fin = inicio + timedelta(hours=1)
        
        response = self.client.post('/api/reservas/', {
            'usuario_id': self.user.id,
            'cabina_id': self.cabina.id,
            'fecha_hora_inicio': inicio.isoformat(),
            'fecha_hora_fin': fin.isoformat(),
        })
        reserva_id = response.data['id']
        self.client.post(f'/api/reservas/{reserva_id}/confirmar/')
        self.client.post('/api/sesiones/', {'reserva_id': reserva_id})
        
        # Listar activas
        response = self.client.get('/api/sesiones/?activas=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['estado'], 'activa')

    def test_calcular_costo_actual(self):
        """Calcular costo actual de sesión."""
        inicio = datetime.now()
        fin = inicio + timedelta(hours=1)
        
        response = self.client.post('/api/reservas/', {
            'usuario_id': self.user.id,
            'cabina_id': self.cabina.id,
            'fecha_hora_inicio': inicio.isoformat(),
            'fecha_hora_fin': fin.isoformat(),
        })
        reserva_id = response.data['id']
        self.client.post(f'/api/reservas/{reserva_id}/confirmar/')
        
        response = self.client.post('/api/sesiones/', {'reserva_id': reserva_id})
        sesion_id = response.data['id']
        
        # Obtener costo actual
        response = self.client.get(f'/api/sesiones/{sesion_id}/costo-actual/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('costo_actual', response.data)
        self.assertGreaterEqual(Decimal(response.data['costo_actual']), Decimal('0'))
