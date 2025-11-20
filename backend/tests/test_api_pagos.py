"""Tests de API REST para Pagos.

IMPORTANTE: No importar modelos antes de override_settings. Para que
override_settings(DATABASES) surta efecto y use SQLite en memoria, los
modelos se importan dentro de setUp luego de aplicar el decorador.
"""
from decimal import Decimal
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from core.domain.models.cabina import EstadoCabina
from core.domain.models.reserva import EstadoReserva
from core.domain.models.sesion import EstadoSesion

User = get_user_model()


@override_settings(
	DATABASES={
		'default': {
			'ENGINE': 'django.db.backends.sqlite3',
			'NAME': ':memory:',
		}
	}
)
class PagoApiTests(APITestCase):
	"""Tests de endpoints de Pagos."""

	def setUp(self):
		# Importar modelos después del override
		from infrastructure.persistence.models import CabinaModel, ReservaModel, SesionModel, PagoModel
		self.CabinaModel = CabinaModel
		self.ReservaModel = ReservaModel
		self.SesionModel = SesionModel
		self.PagoModel = PagoModel

		# Crear usuario
		self.user = User.objects.create_user(
			username='testuser',
			password='testpass123'
		)

		# Obtener token JWT
		response = self.client.post('/api/auth/token/', {
			'username': 'testuser',
			'password': 'testpass123'
		})
		self.token = response.data['access']
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

		# Crear cabina
		self.cabina = self.CabinaModel.objects.create(
			numero=1,
			tipo="BASICA",
			estado=EstadoCabina.DISPONIBLE.value,
			especificaciones={"cpu": "Intel i5", "ram": "8GB"},
			precio_por_hora=Decimal("5.00")
		)

		# Crear reserva
		self.reserva = self.ReservaModel.objects.create(
			usuario=self.user,
			cabina=self.cabina,
			fecha_hora_inicio=timezone.now(),
			fecha_hora_fin=timezone.now(),
			estado=EstadoReserva.CONFIRMADA.value
		)

		# Crear sesión finalizada
		self.sesion = self.SesionModel.objects.create(
			reserva=self.reserva,
			cabina=self.cabina,
			usuario=self.user,
			fecha_hora_inicio=timezone.now(),
			fecha_hora_fin=timezone.now(),
			tiempo_total_minutos=60,
			costo_total=Decimal("5.00"),
			precio_por_hora=Decimal("5.00"),
			estado=EstadoSesion.FINALIZADA.value
		)

	def test_registrar_pago(self):
		"""Registrar un pago para sesión finalizada."""
		response = self.client.post('/api/pagos/', {
			'sesion_id': self.sesion.id,
			'monto': '5.00',
			'metodo_pago': 'efectivo',
			'notas': 'Pago prueba'
		})
		
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data['estado'], 'pendiente')
		self.assertEqual(response.data['monto'], '5.00')
		self.assertEqual(response.data['metodo_pago'], 'efectivo')

	def test_registrar_pago_sesion_no_finalizada(self):
		"""No se puede registrar pago para sesión activa."""
		# Crear una nueva reserva para evitar violar la relación OneToOne (reserva-sesión)
		reserva_activa = self.ReservaModel.objects.create(
			usuario=self.user,
			cabina=self.cabina,
			fecha_hora_inicio=timezone.now(),
			fecha_hora_fin=timezone.now(),
			estado=EstadoReserva.CONFIRMADA.value
		)
		sesion_activa = self.SesionModel.objects.create(
			reserva=reserva_activa,
			cabina=self.cabina,
			usuario=self.user,
			fecha_hora_inicio=timezone.now(),
			fecha_hora_fin=None,
			tiempo_total_minutos=0,
			costo_total=Decimal("0.00"),
			precio_por_hora=Decimal("5.00"),
			estado=EstadoSesion.ACTIVA.value
		)

		response = self.client.post('/api/pagos/', {
			'sesion_id': sesion_activa.id,
			'monto': '5.00',
			'metodo_pago': 'efectivo',
		})

		self.assertEqual(response.status_code, 400)
		self.assertIn('finalizadas', response.data['detail'].lower())

	def test_completar_pago(self):
		"""Completar un pago pendiente."""
		# Registrar pago
		pago = self.PagoModel.objects.create(
			sesion=self.sesion,
			usuario=self.user,
			monto=Decimal("5.00"),
			metodo_pago='efectivo',
			estado='pendiente',
			fecha_pago=timezone.now(),
			notas=""
		)

		# Completar
		response = self.client.post(f'/api/pagos/{pago.id}/completar/', {
			'comprobante_numero': 'REC-TEST-001'
		})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['estado'], 'completado')
		self.assertEqual(response.data['comprobante_numero'], 'REC-TEST-001')

	def test_completar_pago_sin_comprobante_genera_automatico(self):
		"""Completar pago sin comprobante genera uno automático."""
		pago = self.PagoModel.objects.create(
			sesion=self.sesion,
			usuario=self.user,
			monto=Decimal("5.00"),
			metodo_pago='tarjeta',
			estado='pendiente',
			fecha_pago=timezone.now(),
			notas=""
		)

		response = self.client.post(f'/api/pagos/{pago.id}/completar/', {})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['estado'], 'completado')
		self.assertIsNotNone(response.data['comprobante_numero'])
		self.assertIn('COMP-', response.data['comprobante_numero'])

	def test_obtener_historial_usuario(self):
		"""Obtener historial de pagos de usuario."""
		# Crear varios pagos
		self.PagoModel.objects.create(
			sesion=self.sesion,
			usuario=self.user,
			monto=Decimal("5.00"),
			metodo_pago='efectivo',
			estado='completado',
			fecha_pago=timezone.now(),
			comprobante_numero='REC-001',
			notas=""
		)

		response = self.client.get(f'/api/pagos/?usuario_id={self.user.id}')

		self.assertEqual(response.status_code, 200)
		self.assertGreaterEqual(len(response.data), 1)

	def test_generar_comprobante(self):
		"""Generar/obtener comprobante de pago."""
		pago = self.PagoModel.objects.create(
			sesion=self.sesion,
			usuario=self.user,
			monto=Decimal("5.00"),
			metodo_pago='transferencia',
			estado='completado',
			fecha_pago=timezone.now(),
			comprobante_numero='REC-COMP-001',
			notas=""
		)

		response = self.client.get(f'/api/pagos/{pago.id}/comprobante/')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['comprobante_numero'], 'REC-COMP-001')
		self.assertEqual(response.data['sesion_id'], self.sesion.id)

	def test_marcar_pago_fallido(self):
		"""Marcar pago como fallido."""
		pago = self.PagoModel.objects.create(
			sesion=self.sesion,
			usuario=self.user,
			monto=Decimal("5.00"),
			metodo_pago='tarjeta',
			estado='pendiente',
			fecha_pago=timezone.now(),
			notas=""
		)

		response = self.client.post(f'/api/pagos/{pago.id}/marcar-fallido/', {
			'motivo': 'Tarjeta rechazada'
		})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['estado'], 'fallido')
		self.assertIn('Tarjeta rechazada', response.data['notas'])

	def test_reembolsar_pago(self):
		"""Reembolsar pago completado."""
		pago = self.PagoModel.objects.create(
			sesion=self.sesion,
			usuario=self.user,
			monto=Decimal("5.00"),
			metodo_pago='efectivo',
			estado='completado',
			fecha_pago=timezone.now(),
			comprobante_numero='REC-002',
			notas=""
		)

		response = self.client.post(f'/api/pagos/{pago.id}/reembolsar/', {
			'motivo': 'Cliente insatisfecho'
		})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['estado'], 'reembolsado')
		self.assertIn('Cliente insatisfecho', response.data['notas'])

	def test_flujo_completo_sesion_a_pago(self):
		"""Flujo completo: finalizar sesión → registrar pago → completar → comprobante."""
		# 1. Verificar sesión finalizada
		self.assertEqual(self.sesion.estado, EstadoSesion.FINALIZADA.value)

		# 2. Registrar pago
		response = self.client.post('/api/pagos/', {
			'sesion_id': self.sesion.id,
			'monto': '5.00',
			'metodo_pago': 'efectivo',
		})
		self.assertEqual(response.status_code, 201)
		pago_id = response.data['id']

		# 3. Completar pago
		response = self.client.post(f'/api/pagos/{pago_id}/completar/', {})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['estado'], 'completado')

		# 4. Obtener comprobante
		response = self.client.get(f'/api/pagos/{pago_id}/comprobante/')
		self.assertEqual(response.status_code, 200)
		self.assertIsNotNone(response.data['comprobante_numero'])

		# 5. Verificar historial
		response = self.client.get(f'/api/pagos/?usuario_id={self.user.id}')
		self.assertEqual(response.status_code, 200)
		self.assertGreaterEqual(len(response.data), 1)
