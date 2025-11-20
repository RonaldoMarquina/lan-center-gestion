"""Tests unitarios para Pagos (dominio + use cases)."""
import unittest
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from django.utils import timezone

from core.domain.models.pago import Pago, MetodoPago, EstadoPago
from core.domain.models.sesion import Sesion, EstadoSesion
from core.domain.models.reserva import Reserva, EstadoReserva
from core.domain.models.cabina import Cabina, EstadoCabina, TipoCabina
from core.application.use_cases.gestionar_pagos import ProcesarPagos
from core.application.ports.repositories import (
	PagoRepositoryPort,
	SesionRepositoryPort,
	ReservaRepositoryPort,
)


# --- Test Doubles ---
class InMemoryPagoRepository(PagoRepositoryPort):
	def __init__(self):
		self.pagos: dict[int, Pago] = {}
		self.next_id = 1

	def guardar(self, pago: Pago) -> Pago:
		if pago.id == 0:
			pago.id = self.next_id
			self.next_id += 1
		self.pagos[pago.id] = pago
		return pago

	def obtener_por_id(self, pago_id: int) -> Optional[Pago]:
		return self.pagos.get(pago_id)

	def obtener_por_sesion(self, sesion_id: int) -> Optional[Pago]:
		for pago in self.pagos.values():
			if pago.sesion_id == sesion_id:
				return pago
		return None

	def listar_por_usuario(self, usuario_id: int) -> List[Pago]:
		return [p for p in self.pagos.values() if p.usuario_id == usuario_id]

	def listar_por_estado(self, estado: EstadoPago) -> List[Pago]:
		return [p for p in self.pagos.values() if p.estado == estado]

	def listar_por_fecha(self, fecha_desde: datetime, fecha_hasta: datetime) -> List[Pago]:
		return [
			p for p in self.pagos.values()
			if fecha_desde <= p.fecha_pago <= fecha_hasta
		]

	def eliminar(self, pago_id: int) -> None:
		self.pagos.pop(pago_id, None)


class InMemorySesionRepository(SesionRepositoryPort):
	def __init__(self):
		self.sesiones: dict[int, Sesion] = {}
		self.next_id = 1

	def guardar(self, sesion: Sesion) -> Sesion:
		if sesion.id == 0:
			sesion.id = self.next_id
			self.next_id += 1
		self.sesiones[sesion.id] = sesion
		return sesion

	def obtener_por_id(self, sesion_id: int) -> Optional[Sesion]:
		return self.sesiones.get(sesion_id)

	def obtener_por_reserva(self, reserva_id: int) -> Optional[Sesion]:
		for sesion in self.sesiones.values():
			if sesion.reserva_id == reserva_id:
				return sesion
		return None

	def listar_por_usuario(self, usuario_id: int) -> List[Sesion]:
		return [s for s in self.sesiones.values() if s.usuario_id == usuario_id]

	def listar_por_cabina(self, cabina_id: int) -> List[Sesion]:
		return [s for s in self.sesiones.values() if s.cabina_id == cabina_id]

	def listar_activas(self) -> List[Sesion]:
		return [s for s in self.sesiones.values() if s.estado == EstadoSesion.ACTIVA]

	def eliminar(self, sesion_id: int) -> None:
		self.sesiones.pop(sesion_id, None)


class InMemoryReservaRepository(ReservaRepositoryPort):
	def __init__(self):
		self.reservas: dict[int, Reserva] = {}
		self.next_id = 1

	def guardar(self, reserva: Reserva) -> Reserva:
		if reserva.id == 0:
			reserva.id = self.next_id
			self.next_id += 1
		self.reservas[reserva.id] = reserva
		return reserva

	def obtener_por_id(self, reserva_id: int) -> Optional[Reserva]:
		return self.reservas.get(reserva_id)

	def listar_por_usuario(self, usuario_id: int) -> List[Reserva]:
		return [r for r in self.reservas.values() if r.usuario_id == usuario_id]

	def listar_por_cabina(self, cabina_id: int) -> List[Reserva]:
		return [r for r in self.reservas.values() if r.cabina_id == cabina_id]

	def listar_por_estado(self, estado: EstadoReserva) -> List[Reserva]:
		return [r for r in self.reservas.values() if r.estado == estado]

	def buscar_conflictos(self, cabina_id: int, inicio: datetime, fin: datetime, reserva_id: Optional[int] = None) -> List[Reserva]:
		return []

	def eliminar(self, reserva_id: int) -> None:
		self.reservas.pop(reserva_id, None)


# --- Tests Dominio Pago ---
class TestPagoDominio(unittest.TestCase):
	def test_crear_pago_valido(self):
		pago = Pago(
			id=1,
			sesion_id=1,
			usuario_id=1,
			monto=Decimal("15.50"),
			metodo_pago=MetodoPago.EFECTIVO,
			estado=EstadoPago.PENDIENTE,
			fecha_pago=timezone.now(),
			comprobante_numero=None,
			notas="Primera compra",
		)
		self.assertEqual(pago.estado, EstadoPago.PENDIENTE)
		self.assertEqual(pago.monto, Decimal("15.50"))

	def test_completar_pago(self):
		pago = Pago(
			id=1,
			sesion_id=1,
			usuario_id=1,
			monto=Decimal("20.00"),
			metodo_pago=MetodoPago.TARJETA,
			estado=EstadoPago.PENDIENTE,
			fecha_pago=timezone.now(),
			comprobante_numero=None,
			notas="",
		)
		pago.completar("REC-001")
		self.assertEqual(pago.estado, EstadoPago.COMPLETADO)
		self.assertEqual(pago.comprobante_numero, "REC-001")

	def test_marcar_fallido(self):
		pago = Pago(
			id=1,
			sesion_id=1,
			usuario_id=1,
			monto=Decimal("10.00"),
			metodo_pago=MetodoPago.TRANSFERENCIA,
			estado=EstadoPago.PENDIENTE,
			fecha_pago=timezone.now(),
			comprobante_numero=None,
			notas="",
		)
		pago.marcar_fallido("Fondos insuficientes")
		self.assertEqual(pago.estado, EstadoPago.FALLIDO)
		self.assertIn("Fondos insuficientes", pago.notas)

	def test_reembolsar_pago(self):
		pago = Pago(
			id=1,
			sesion_id=1,
			usuario_id=1,
			monto=Decimal("25.00"),
			metodo_pago=MetodoPago.EFECTIVO,
			estado=EstadoPago.COMPLETADO,
			fecha_pago=timezone.now(),
			comprobante_numero="REC-002",
			notas="",
		)
		pago.reembolsar("Servicio no prestado")
		self.assertEqual(pago.estado, EstadoPago.REEMBOLSADO)
		self.assertIn("Servicio no prestado", pago.notas)

	def test_generar_numero_comprobante(self):
		pago = Pago(
			id=123,
			sesion_id=1,
			usuario_id=1,
			monto=Decimal("30.00"),
			metodo_pago=MetodoPago.BILLETERA_DIGITAL,
			estado=EstadoPago.PENDIENTE,
			fecha_pago=timezone.now(),
			comprobante_numero=None,
			notas="",
		)
		comprobante = pago.generar_numero_comprobante()
		self.assertTrue(comprobante.startswith("COMP-"))
		self.assertIn("123", comprobante)

	def test_monto_invalido(self):
		with self.assertRaises(ValueError):
			Pago(
				id=1,
				sesion_id=1,
				usuario_id=1,
				monto=Decimal("-5.00"),  # Negativo
				metodo_pago=MetodoPago.EFECTIVO,
				estado=EstadoPago.PENDIENTE,
				fecha_pago=timezone.now(),
				comprobante_numero=None,
				notas="",
			)


# --- Tests Use Case ProcesarPagos ---
class TestProcesarPagosUseCase(unittest.TestCase):
	def setUp(self):
		self.pago_repo = InMemoryPagoRepository()
		self.sesion_repo = InMemorySesionRepository()
		self.reserva_repo = InMemoryReservaRepository()
		self.use_case = ProcesarPagos(self.pago_repo, self.sesion_repo, self.reserva_repo)

		# Crear sesión finalizada
		self.sesion_finalizada = Sesion(
			id=1,
			reserva_id=1,
			cabina_id=1,
			usuario_id=1,
			fecha_hora_inicio=timezone.now(),
			fecha_hora_fin=timezone.now(),
			tiempo_total_minutos=60,
			costo_total=Decimal("5.00"),
			precio_por_hora=Decimal("5.00"),
			estado=EstadoSesion.FINALIZADA,
		)
		self.sesion_repo.guardar(self.sesion_finalizada)

	def test_registrar_pago_exitoso(self):
		pago = self.use_case.registrar_pago(
			sesion_id=1,
			monto=Decimal("5.00"),
			metodo_pago=MetodoPago.EFECTIVO,
		)
		self.assertEqual(pago.estado, EstadoPago.PENDIENTE)
		self.assertEqual(pago.sesion_id, 1)

	def test_registrar_pago_sesion_no_existe(self):
		with self.assertRaises(ValueError) as ctx:
			self.use_case.registrar_pago(
				sesion_id=999,
				monto=Decimal("10.00"),
				metodo_pago=MetodoPago.TARJETA,
			)
		self.assertIn("no existe", str(ctx.exception))

	def test_registrar_pago_sesion_no_finalizada(self):
		sesion_activa = Sesion(
			id=2,
			reserva_id=2,
			cabina_id=1,
			usuario_id=1,
			fecha_hora_inicio=timezone.now(),
			fecha_hora_fin=None,
			tiempo_total_minutos=0,
			costo_total=Decimal("0.00"),
			precio_por_hora=Decimal("5.00"),
			estado=EstadoSesion.ACTIVA,
		)
		self.sesion_repo.guardar(sesion_activa)

		with self.assertRaises(ValueError) as ctx:
			self.use_case.registrar_pago(
				sesion_id=2,
				monto=Decimal("5.00"),
				metodo_pago=MetodoPago.EFECTIVO,
			)
		self.assertIn("finalizadas", str(ctx.exception))

	def test_completar_pago(self):
		pago = self.use_case.registrar_pago(
			sesion_id=1,
			monto=Decimal("5.00"),
			metodo_pago=MetodoPago.EFECTIVO,
		)
		
		pago_completado = self.use_case.completar_pago(pago.id, "REC-123")
		self.assertEqual(pago_completado.estado, EstadoPago.COMPLETADO)
		self.assertEqual(pago_completado.comprobante_numero, "REC-123")

	def test_completar_pago_genera_comprobante_automatico(self):
		pago = self.use_case.registrar_pago(
			sesion_id=1,
			monto=Decimal("5.00"),
			metodo_pago=MetodoPago.EFECTIVO,
		)
		
		pago_completado = self.use_case.completar_pago(pago.id)
		self.assertEqual(pago_completado.estado, EstadoPago.COMPLETADO)
		self.assertIsNotNone(pago_completado.comprobante_numero)

	def test_obtener_historial_usuario(self):
		pago1 = self.use_case.registrar_pago(1, Decimal("5.00"), MetodoPago.EFECTIVO)
		
		sesion2 = Sesion(
			id=2,
			reserva_id=2,
			cabina_id=1,
			usuario_id=1,
			fecha_hora_inicio=timezone.now(),
			fecha_hora_fin=timezone.now(),
			tiempo_total_minutos=120,
			costo_total=Decimal("10.00"),
			precio_por_hora=Decimal("5.00"),
			estado=EstadoSesion.FINALIZADA,
		)
		self.sesion_repo.guardar(sesion2)
		pago2 = self.use_case.registrar_pago(2, Decimal("10.00"), MetodoPago.TARJETA)

		historial = self.use_case.obtener_historial_usuario(1)
		self.assertEqual(len(historial), 2)

	def test_generar_comprobante(self):
		pago = self.use_case.registrar_pago(1, Decimal("5.00"), MetodoPago.EFECTIVO)
		pago_completado = self.use_case.completar_pago(pago.id, "REC-456")

		comprobante = self.use_case.generar_comprobante(pago_completado.id)
		self.assertEqual(comprobante, "REC-456")


if __name__ == "__main__":
	unittest.main()
