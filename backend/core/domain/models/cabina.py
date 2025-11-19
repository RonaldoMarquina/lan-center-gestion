"""Modelo de dominio para la gestión de cabinas.

Esta entidad encapsula las reglas de negocio relacionadas con el ciclo de vida
de una cabina en el LAN Center (creación, ocupación, liberación, mantenimiento,
desactivación). No depende de frameworks ni de detalles de infraestructura.

Requisitos funcionales cubiertos (parcial):
 - RF06 Creación de Cabinas (atributos básicos y validaciones)
 - RF07 Modificación de Cabinas (métodos permiten mutar estado y precio)
 - RF08 Cambio de Estado Manual (métodos de transición de estado)
 - RF09 Eliminación de Cabinas (se controlará en el repositorio: no eliminar si ocupada)
 - RF10 Panel de Control (estados normalizados para consulta)

Escenarios y reglas clave:
 - Una cabina sólo puede pasar a OCUPADA si está DISPONIBLE.
 - No se puede poner en mantenimiento una cabina OCUPADA (debe liberarse antes).
 - Al finalizar mantenimiento vuelve a DISPONIBLE (si estaba en MANTENIMIENTO).
 - Un cambio a DESACTIVADA sólo es válido si NO está OCUPADA.
 - Precio por hora debe ser positivo.
 - Número de cabina debe ser entero positivo y único (validado fuera, en el caso de uso / repositorio).

La lógica se implementa mediante métodos que realizan validaciones y lanzan
ValueError ante violaciones de reglas de negocio simples. Para escalabilidad,
en el futuro se podría introducir un sistema de excepciones de dominio más rico.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class TipoCabina(Enum):
	"""Clasificación de la cabina según características y tarifa base.

	Permite aplicar políticas de precios diferenciadas en el futuro.
	"""

	BASICA = "BASICA"
	GAMER = "GAMER"
	VIP = "VIP"


class EstadoCabina(Enum):
	"""Estados válidos del ciclo de vida operacional de una cabina."""

	DISPONIBLE = "DISPONIBLE"
	OCUPADA = "OCUPADA"
	MANTENIMIENTO = "MANTENIMIENTO"
	DESACTIVADA = "DESACTIVADA"


@dataclass
class Cabina:
	"""Entidad de dominio Cabina.

	Attributes:
		id: Identificador único (asignado por persistencia). Puede ser None antes de guardar.
		numero: Número visible/operativo para referencia humana (único en el sistema).
		tipo: Tipo de cabina (BASICA, GAMER, VIP).
		estado: Estado operativo actual.
		especificaciones: Detalles técnicos (ej. CPU, GPU, RAM) u otros metadatos.
		precio_por_hora: Tarifa vigente para cálculo de costos.
	"""

	id: Optional[int]
	numero: int
	tipo: TipoCabina
	estado: EstadoCabina
	especificaciones: Dict[str, Any]
	precio_por_hora: float

	def __post_init__(self) -> None:
		"""Validaciones iniciales básicas de invariantes."""
		if self.numero <= 0:
			raise ValueError("El número de cabina debe ser positivo")
		if self.precio_por_hora <= 0:
			raise ValueError("El precio por hora debe ser positivo")
		if not isinstance(self.especificaciones, dict):
			raise ValueError("Las especificaciones deben ser un diccionario")

	# Transiciones de estado -------------------------------
	def ocupar(self) -> None:
		"""Marca la cabina como OCUPADA si está DISPONIBLE.

		Raises:
			ValueError: Si la cabina no está disponible o está desactivada/mantenimiento.
		"""
		if self.estado != EstadoCabina.DISPONIBLE:
			raise ValueError(
				f"No se puede ocupar una cabina en estado {self.estado.value}"
			)
		self.estado = EstadoCabina.OCUPADA

	def liberar(self) -> None:
		"""Libera la cabina pasando a DISPONIBLE si está OCUPADA.

		Raises:
			ValueError: Si la cabina no está ocupada.
		"""
		if self.estado != EstadoCabina.OCUPADA:
			raise ValueError(
				f"Sólo se puede liberar una cabina OCUPADA (actual: {self.estado.value})"
			)
		self.estado = EstadoCabina.DISPONIBLE

	def iniciar_mantenimiento(self) -> None:
		"""Coloca la cabina en MANTENIMIENTO si no está OCUPADA.

		Raises:
			ValueError: Si la cabina está ocupada o desactivada.
		"""
		if self.estado == EstadoCabina.OCUPADA:
			raise ValueError("Debe liberarse la cabina antes de mantenimiento")
		if self.estado == EstadoCabina.DESACTIVADA:
			raise ValueError("No se puede dar mantenimiento a una cabina desactivada")
		self.estado = EstadoCabina.MANTENIMIENTO

	def finalizar_mantenimiento(self) -> None:
		"""Regresa la cabina a DISPONIBLE si está en MANTENIMIENTO.

		Raises:
			ValueError: Si la cabina no está en mantenimiento.
		"""
		if self.estado != EstadoCabina.MANTENIMIENTO:
			raise ValueError(
				f"La cabina debe estar en MANTENIMIENTO para finalizar (actual: {self.estado.value})"
			)
		self.estado = EstadoCabina.DISPONIBLE

	def desactivar(self) -> None:
		"""Desactiva la cabina (estado DESACTIVADA) si no está OCUPADA.

		Raises:
			ValueError: Si la cabina está ocupada.
		"""
		if self.estado == EstadoCabina.OCUPADA:
			raise ValueError("No se puede desactivar una cabina ocupada")
		self.estado = EstadoCabina.DESACTIVADA

	def activar(self) -> None:
		"""Reactiva la cabina si está DESACTIVADA devolviéndola a DISPONIBLE.

		Raises:
			ValueError: Si la cabina no está desactivada.
		"""
		if self.estado != EstadoCabina.DESACTIVADA:
			raise ValueError("Sólo se puede activar una cabina desactivada")
		self.estado = EstadoCabina.DISPONIBLE

	# Otras operaciones ------------------------------------
	def actualizar_precio(self, nuevo_precio: float) -> None:
		"""Actualiza la tarifa por hora.

		Raises:
			ValueError: Si el precio no es positivo.
		"""
		if nuevo_precio <= 0:
			raise ValueError("El precio debe ser positivo")
		self.precio_por_hora = nuevo_precio

	def to_dict(self) -> Dict[str, Any]:
		"""Representación simple para serialización fuera de la capa de dominio.

		Nota: La conversión a formatos específicos (JSON, ORM) debe manejarse en
		capas superiores (application/infrastructure) para mantener independencia.
		"""
		return {
			"id": self.id,
			"numero": self.numero,
			"tipo": self.tipo.value,
			"estado": self.estado.value,
			"especificaciones": self.especificaciones,
			"precio_por_hora": self.precio_por_hora,
		}

