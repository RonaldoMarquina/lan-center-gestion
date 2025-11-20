"""Entidad de dominio Cabina: estado y operaciones básicas."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class TipoCabina(Enum):
	"""Tipos de cabina."""

	BASICA = "BASICA"
	GAMER = "GAMER"
	VIP = "VIP"


class EstadoCabina(Enum):
	"""Estados de la cabina."""

	DISPONIBLE = "DISPONIBLE"
	OCUPADA = "OCUPADA"
	MANTENIMIENTO = "MANTENIMIENTO"
	DESACTIVADA = "DESACTIVADA"


@dataclass
class Cabina:
	"""Cabina con número, tipo, estado, specs y precio."""

	id: Optional[int]
	numero: int
	tipo: TipoCabina
	estado: EstadoCabina
	especificaciones: Dict[str, Any]
	precio_por_hora: float

	def __post_init__(self) -> None:
		"""Validaciones básicas."""
		if self.numero <= 0:
			raise ValueError("El número de cabina debe ser positivo")
		if self.precio_por_hora <= 0:
			raise ValueError("El precio por hora debe ser positivo")
		if not isinstance(self.especificaciones, dict):
			raise ValueError("Las especificaciones deben ser un diccionario")

	# Transiciones de estado -------------------------------
	def ocupar(self) -> None:
		"""Pone estado OCUPADA si está DISPONIBLE."""
		if self.estado != EstadoCabina.DISPONIBLE:
			raise ValueError(
				f"No se puede ocupar una cabina en estado {self.estado.value}"
			)
		self.estado = EstadoCabina.OCUPADA

	def liberar(self) -> None:
		"""Pasa a DISPONIBLE si está OCUPADA."""
		if self.estado != EstadoCabina.OCUPADA:
			raise ValueError(
				f"Sólo se puede liberar una cabina OCUPADA (actual: {self.estado.value})"
			)
		self.estado = EstadoCabina.DISPONIBLE

	def iniciar_mantenimiento(self) -> None:
		"""Pone estado MANTENIMIENTO si no está OCUPADA."""
		if self.estado == EstadoCabina.OCUPADA:
			raise ValueError("Debe liberarse la cabina antes de mantenimiento")
		if self.estado == EstadoCabina.DESACTIVADA:
			raise ValueError("No se puede dar mantenimiento a una cabina desactivada")
		self.estado = EstadoCabina.MANTENIMIENTO

	def finalizar_mantenimiento(self) -> None:
		"""De MANTENIMIENTO a DISPONIBLE."""
		if self.estado != EstadoCabina.MANTENIMIENTO:
			raise ValueError(
				f"La cabina debe estar en MANTENIMIENTO para finalizar (actual: {self.estado.value})"
			)
		self.estado = EstadoCabina.DISPONIBLE

	def desactivar(self) -> None:
		"""A DESACTIVADA si no está OCUPADA."""
		if self.estado == EstadoCabina.OCUPADA:
			raise ValueError("No se puede desactivar una cabina ocupada")
		self.estado = EstadoCabina.DESACTIVADA

	def activar(self) -> None:
		"""De DESACTIVADA a DISPONIBLE."""
		if self.estado != EstadoCabina.DESACTIVADA:
			raise ValueError("Sólo se puede activar una cabina desactivada")
		self.estado = EstadoCabina.DISPONIBLE

	# Otras operaciones ------------------------------------
	def actualizar_precio(self, nuevo_precio: float) -> None:
		"""Actualiza precio por hora (debe ser > 0)."""
		if nuevo_precio <= 0:
			raise ValueError("El precio debe ser positivo")
		self.precio_por_hora = nuevo_precio

	def to_dict(self) -> Dict[str, Any]:
		"""Dict simple de la cabina."""
		return {
			"id": self.id,
			"numero": self.numero,
			"tipo": self.tipo.value,
			"estado": self.estado.value,
			"especificaciones": self.especificaciones,
			"precio_por_hora": self.precio_por_hora,
		}

