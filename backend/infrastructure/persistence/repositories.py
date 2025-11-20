"""Adapter repositorio Cabina, Reserva y Sesion (Django ORM)."""

from typing import List, Optional
from datetime import datetime

from django.db import transaction
from django.db.models import Q

from core.application.ports.repositories import (
	CabinaRepositoryPort,
	ReservaRepositoryPort,
	SesionRepositoryPort,
	PagoRepositoryPort,
)
from core.domain.models.cabina import Cabina, EstadoCabina
from core.domain.models.reserva import Reserva, EstadoReserva
from core.domain.models.sesion import Sesion, EstadoSesion
from core.domain.models.pago import Pago, EstadoPago
from .models import CabinaModel, ReservaModel, SesionModel, PagoModel


class DjangoCabinaRepository(CabinaRepositoryPort):
	"""Implementa puerto usando CabinaModel."""

	@transaction.atomic
	def guardar(self, cabina: Cabina) -> Cabina:  # type: ignore[override]
		if cabina.id:
			model = CabinaModel.objects.get(id=cabina.id)
			model.numero = cabina.numero
			model.tipo = cabina.tipo.value
			model.estado = cabina.estado.value
			model.especificaciones = cabina.especificaciones
			model.precio_por_hora = cabina.precio_por_hora
			model.save()
			return model.to_domain()
		# create
		model = CabinaModel.from_domain(cabina)
		model.save()
		return model.to_domain()

	def obtener_por_id(self, cabina_id: int) -> Optional[Cabina]:  # type: ignore[override]
		try:
			return CabinaModel.objects.get(id=cabina_id).to_domain()
		except CabinaModel.DoesNotExist:
			return None

	def buscar_por_numero(self, numero: int) -> Optional[Cabina]:  # type: ignore[override]
		try:
			return CabinaModel.objects.get(numero=numero).to_domain()
		except CabinaModel.DoesNotExist:
			return None

	def buscar_por_estado(self, estado: EstadoCabina) -> List[Cabina]:  # type: ignore[override]
		return [m.to_domain() for m in CabinaModel.objects.filter(estado=estado.value)]

	def listar_todas(self) -> List[Cabina]:  # type: ignore[override]
		return [m.to_domain() for m in CabinaModel.objects.all()]

	@transaction.atomic
	def eliminar(self, cabina_id: int) -> None:  # type: ignore[override]
		try:
			model = CabinaModel.objects.get(id=cabina_id)
		except CabinaModel.DoesNotExist:
			return
		if model.estado == EstadoCabina.OCUPADA.value:
			raise ValueError("No eliminar cabina ocupada")
		model.delete()


class DjangoReservaRepository(ReservaRepositoryPort):
	"""Implementa puerto usando ReservaModel."""

	@transaction.atomic
	def guardar(self, reserva: Reserva) -> Reserva:  # type: ignore[override]
		if reserva.id:
			model = ReservaModel.objects.get(id=reserva.id)
			model.usuario_id = reserva.usuario_id
			model.cabina_id = reserva.cabina_id
			model.fecha_hora_inicio = reserva.fecha_hora_inicio
			model.fecha_hora_fin = reserva.fecha_hora_fin
			model.estado = reserva.estado.value
			model.save()
			return model.to_domain()
		# create
		model = ReservaModel.from_domain(reserva)
		model.save()
		return model.to_domain()

	def obtener_por_id(self, reserva_id: int) -> Optional[Reserva]:  # type: ignore[override]
		try:
			return ReservaModel.objects.get(id=reserva_id).to_domain()
		except ReservaModel.DoesNotExist:
			return None

	def listar_por_usuario(self, usuario_id: int) -> List[Reserva]:  # type: ignore[override]
		return [m.to_domain() for m in ReservaModel.objects.filter(usuario_id=usuario_id)]

	def listar_por_cabina(self, cabina_id: int) -> List[Reserva]:  # type: ignore[override]
		return [m.to_domain() for m in ReservaModel.objects.filter(cabina_id=cabina_id)]

	def listar_por_estado(self, estado: EstadoReserva) -> List[Reserva]:  # type: ignore[override]
		return [m.to_domain() for m in ReservaModel.objects.filter(estado=estado.value)]

	def buscar_conflictos(
		self,
		cabina_id: int,
		inicio: datetime,
		fin: datetime
	) -> List[Reserva]:  # type: ignore[override]
		"""Busca reservas que solapen con el rango."""
		conflictos = ReservaModel.objects.filter(
			cabina_id=cabina_id,
			estado__in=[
				EstadoReserva.PENDIENTE.value,
				EstadoReserva.CONFIRMADA.value,
				EstadoReserva.EN_CURSO.value,
			]
		).filter(
			Q(fecha_hora_inicio__lt=fin) & Q(fecha_hora_fin__gt=inicio)
		)
		return [m.to_domain() for m in conflictos]

	@transaction.atomic
	def eliminar(self, reserva_id: int) -> None:  # type: ignore[override]
		try:
			model = ReservaModel.objects.get(id=reserva_id)
			model.delete()
		except ReservaModel.DoesNotExist:
			pass


class DjangoSesionRepository(SesionRepositoryPort):
	"""Implementa puerto usando SesionModel."""

	@transaction.atomic
	def guardar(self, sesion: Sesion) -> Sesion:  # type: ignore[override]
		if sesion.id:
			model = SesionModel.objects.get(id=sesion.id)
			model.reserva_id = sesion.reserva_id
			model.cabina_id = sesion.cabina_id
			model.usuario_id = sesion.usuario_id
			model.fecha_hora_inicio = sesion.fecha_hora_inicio
			model.fecha_hora_fin = sesion.fecha_hora_fin
			model.tiempo_total_minutos = sesion.tiempo_total_minutos
			model.costo_total = sesion.costo_total
			model.precio_por_hora = sesion.precio_por_hora
			model.estado = sesion.estado.value
			model.save()
			return model.to_domain()
		# create
		model = SesionModel.from_domain(sesion)
		model.save()
		return model.to_domain()

	def obtener_por_id(self, sesion_id: int) -> Optional[Sesion]:  # type: ignore[override]
		try:
			return SesionModel.objects.get(id=sesion_id).to_domain()
		except SesionModel.DoesNotExist:
			return None

	def obtener_por_reserva(self, reserva_id: int) -> Optional[Sesion]:  # type: ignore[override]
		try:
			return SesionModel.objects.get(reserva_id=reserva_id).to_domain()
		except SesionModel.DoesNotExist:
			return None

	def listar_por_usuario(self, usuario_id: int) -> List[Sesion]:  # type: ignore[override]
		return [m.to_domain() for m in SesionModel.objects.filter(usuario_id=usuario_id)]

	def listar_por_cabina(self, cabina_id: int) -> List[Sesion]:  # type: ignore[override]
		return [m.to_domain() for m in SesionModel.objects.filter(cabina_id=cabina_id)]

	def listar_activas(self) -> List[Sesion]:  # type: ignore[override]
		return [
			m.to_domain()
			for m in SesionModel.objects.filter(estado=EstadoSesion.ACTIVA.value)
		]

	@transaction.atomic
	def eliminar(self, sesion_id: int) -> None:  # type: ignore[override]
		try:
			model = SesionModel.objects.get(id=sesion_id)
			model.delete()
		except SesionModel.DoesNotExist:
			pass


class DjangoPagoRepository(PagoRepositoryPort):
	"""Implementa puerto usando PagoModel."""

	@transaction.atomic
	def guardar(self, pago: Pago) -> Pago:  # type: ignore[override]
		if pago.id:
			model = PagoModel.objects.get(id=pago.id)
			model.sesion_id = pago.sesion_id
			model.usuario_id = pago.usuario_id
			model.monto = pago.monto
			model.metodo_pago = pago.metodo_pago.value.lower()
			model.estado = pago.estado.value.lower()
			model.fecha_pago = pago.fecha_pago
			model.comprobante_numero = pago.comprobante_numero
			model.notas = pago.notas
			model.save()
			return model.to_domain()
		# create
		model = PagoModel.from_domain(pago)
		model.save()
		return model.to_domain()

	def obtener_por_id(self, pago_id: int) -> Optional[Pago]:  # type: ignore[override]
		try:
			return PagoModel.objects.get(id=pago_id).to_domain()
		except PagoModel.DoesNotExist:
			return None

	def obtener_por_sesion(self, sesion_id: int) -> Optional[Pago]:  # type: ignore[override]
		try:
			return PagoModel.objects.get(sesion_id=sesion_id).to_domain()
		except PagoModel.DoesNotExist:
			return None

	def listar_por_usuario(self, usuario_id: int) -> List[Pago]:  # type: ignore[override]
		return [m.to_domain() for m in PagoModel.objects.filter(usuario_id=usuario_id)]

	def listar_por_estado(self, estado: EstadoPago) -> List[Pago]:  # type: ignore[override]
		return [
			m.to_domain()
			for m in PagoModel.objects.filter(estado=estado.value.lower())
		]

	def listar_por_fecha(self, fecha_desde: datetime, fecha_hasta: datetime) -> List[Pago]:  # type: ignore[override]
		return [
			m.to_domain()
			for m in PagoModel.objects.filter(
				fecha_pago__gte=fecha_desde, fecha_pago__lte=fecha_hasta
			)
		]

	@transaction.atomic
	def eliminar(self, pago_id: int) -> None:  # type: ignore[override]
		try:
			model = PagoModel.objects.get(id=pago_id)
			model.delete()
		except PagoModel.DoesNotExist:
			pass
