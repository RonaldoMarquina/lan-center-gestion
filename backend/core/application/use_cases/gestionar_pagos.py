"""Casos de uso para gestión de pagos."""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from django.utils import timezone

from core.domain.models.pago import Pago, MetodoPago, EstadoPago
from core.domain.models.sesion import EstadoSesion
from core.application.ports.repositories import (
	PagoRepositoryPort,
	SesionRepositoryPort,
	ReservaRepositoryPort,
)


class ProcesarPagos:
	"""Orquesta operaciones de procesamiento de pagos."""

	def __init__(
		self,
		pago_repository: PagoRepositoryPort,
		sesion_repository: SesionRepositoryPort,
		reserva_repository: ReservaRepositoryPort,
	):
		self.pago_repository = pago_repository
		self.sesion_repository = sesion_repository
		self.reserva_repository = reserva_repository

	def registrar_pago(
		self,
		sesion_id: int,
		monto: Decimal,
		metodo_pago: MetodoPago,
		notas: Optional[str] = None,
	) -> Pago:
		"""Registrar nuevo pago para sesión finalizada."""
		# Validar sesión existe y está finalizada
		sesion = self.sesion_repository.obtener_por_id(sesion_id)
		if not sesion:
			raise ValueError(f"Sesión {sesion_id} no existe")

		if sesion.estado != EstadoSesion.FINALIZADA:
			raise ValueError(
				"Solo se pueden registrar pagos para sesiones finalizadas"
			)

		# Validar que no exista ya un pago para esta sesión
		pago_existente = self.pago_repository.obtener_por_sesion(sesion_id)
		if pago_existente:
			raise ValueError(f"Ya existe un pago para la sesión {sesion_id}")

		# Crear pago
		pago = Pago(
			id=0,
			sesion_id=sesion_id,
			usuario_id=sesion.usuario_id,
			monto=monto,
			metodo_pago=metodo_pago,
			estado=EstadoPago.PENDIENTE,
			fecha_pago=timezone.now(),
			comprobante_numero=None,
			notas=notas or "",
		)

		return self.pago_repository.guardar(pago)

	def completar_pago(self, pago_id: int, comprobante_numero: Optional[str] = None) -> Pago:
		"""Marcar pago como completado."""
		pago = self.pago_repository.obtener_por_id(pago_id)
		if not pago:
			raise ValueError(f"Pago {pago_id} no encontrado")

		# Si no se proporciona comprobante, generar uno
		if not comprobante_numero:
			comprobante_numero = pago.generar_numero_comprobante()

		pago.completar(comprobante_numero)
		return self.pago_repository.guardar(pago)

	def marcar_pago_fallido(self, pago_id: int, motivo: str) -> Pago:
		"""Marcar pago como fallido."""
		pago = self.pago_repository.obtener_por_id(pago_id)
		if not pago:
			raise ValueError(f"Pago {pago_id} no encontrado")

		pago.marcar_fallido(motivo)
		return self.pago_repository.guardar(pago)

	def reembolsar_pago(self, pago_id: int, motivo: str) -> Pago:
		"""Reembolsar pago completado."""
		pago = self.pago_repository.obtener_por_id(pago_id)
		if not pago:
			raise ValueError(f"Pago {pago_id} no encontrado")

		pago.reembolsar(motivo)
		return self.pago_repository.guardar(pago)

	def obtener_pago(self, pago_id: int) -> Optional[Pago]:
		"""Obtener pago por id."""
		return self.pago_repository.obtener_por_id(pago_id)

	def obtener_historial_usuario(self, usuario_id: int) -> List[Pago]:
		"""Obtener historial de pagos de usuario."""
		return self.pago_repository.listar_por_usuario(usuario_id)

	def obtener_pagos_pendientes(self) -> List[Pago]:
		"""Listar pagos pendientes."""
		return self.pago_repository.listar_por_estado(EstadoPago.PENDIENTE)

	def obtener_pagos_por_fecha(
		self, fecha_desde: datetime, fecha_hasta: datetime
	) -> List[Pago]:
		"""Obtener pagos en rango de fechas."""
		return self.pago_repository.listar_por_fecha(fecha_desde, fecha_hasta)

	def generar_comprobante(self, pago_id: int, prefijo: str = "REC") -> str:
		"""Generar número de comprobante para pago."""
		pago = self.pago_repository.obtener_por_id(pago_id)
		if not pago:
			raise ValueError(f"Pago {pago_id} no encontrado")

		if pago.estado != EstadoPago.COMPLETADO:
			raise ValueError("Solo se puede generar comprobante para pagos completados")

		if not pago.comprobante_numero:
			comprobante = pago.generar_numero_comprobante(prefijo)
			pago.comprobante_numero = comprobante
			self.pago_repository.guardar(pago)
			return comprobante

		return pago.comprobante_numero
