"""Puerto repositorio Cabina (contrato)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from core.domain.models.cabina import Cabina, EstadoCabina


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

