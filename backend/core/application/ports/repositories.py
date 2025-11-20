"""Puerto repositorio Cabina (contrato)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from core.domain.models.cabina import Cabina, EstadoCabina
from core.domain.models.reserva import Reserva, EstadoReserva
from core.domain.models.sesion import Sesion, EstadoSesion
from datetime import datetime


class CabinaRepositoryPort(ABC):
	"""Operaciones CRUD y consultas de Cabina."""

	@abstractmethod
	def guardar(self, cabina: Cabina) -> Cabina:
		"""Crear/actualizar cabina."""
		raise NotImplementedError

	@abstractmethod
	def obtener_por_id(self, cabina_id: int) -> Optional[Cabina]:
		"""Por id."""
		raise NotImplementedError

	@abstractmethod
	def buscar_por_numero(self, numero: int) -> Optional[Cabina]:
		"""Por numero."""
		raise NotImplementedError

	@abstractmethod
	def buscar_por_estado(self, estado: EstadoCabina) -> List[Cabina]:
		"""Por estado."""
		raise NotImplementedError

	@abstractmethod
	def listar_todas(self) -> List[Cabina]:
		"""Todas."""
		raise NotImplementedError

	@abstractmethod
	def eliminar(self, cabina_id: int) -> None:
		"""Eliminar (no si OCUPADA)."""
		raise NotImplementedError


class ReservaRepositoryPort(ABC):
	"""Operaciones CRUD y consultas de Reserva."""

	@abstractmethod
	def guardar(self, reserva: Reserva) -> Reserva:
		"""Crear/actualizar reserva."""
		raise NotImplementedError

	@abstractmethod
	def obtener_por_id(self, reserva_id: int) -> Optional[Reserva]:
		"""Por id."""
		raise NotImplementedError

	@abstractmethod
	def listar_por_usuario(self, usuario_id: int) -> List[Reserva]:
		"""Por usuario."""
		raise NotImplementedError

	@abstractmethod
	def listar_por_cabina(self, cabina_id: int) -> List[Reserva]:
		"""Por cabina."""
		raise NotImplementedError

	@abstractmethod
	def listar_por_estado(self, estado: EstadoReserva) -> List[Reserva]:
		"""Por estado."""
		raise NotImplementedError

	@abstractmethod
	def buscar_conflictos(self, cabina_id: int, inicio: datetime, fin: datetime) -> List[Reserva]:
		"""Buscar reservas que solapen con el rango de tiempo."""
		raise NotImplementedError

	@abstractmethod
	def eliminar(self, reserva_id: int) -> None:
		"""Eliminar reserva."""
		raise NotImplementedError


class SesionRepositoryPort(ABC):
	"""Operaciones CRUD y consultas de Sesion."""

	@abstractmethod
	def guardar(self, sesion: Sesion) -> Sesion:
		"""Crear/actualizar sesión."""
		raise NotImplementedError

	@abstractmethod
	def obtener_por_id(self, sesion_id: int) -> Optional[Sesion]:
		"""Por id."""
		raise NotImplementedError

	@abstractmethod
	def obtener_por_reserva(self, reserva_id: int) -> Optional[Sesion]:
		"""Por reserva."""
		raise NotImplementedError

	@abstractmethod
	def listar_por_usuario(self, usuario_id: int) -> List[Sesion]:
		"""Por usuario."""
		raise NotImplementedError

	@abstractmethod
	def listar_por_cabina(self, cabina_id: int) -> List[Sesion]:
		"""Por cabina."""
		raise NotImplementedError

	@abstractmethod
	def listar_activas(self) -> List[Sesion]:
		"""Sesiones activas."""
		raise NotImplementedError

	@abstractmethod
	def eliminar(self, sesion_id: int) -> None:
		"""Eliminar sesión."""
		raise NotImplementedError
