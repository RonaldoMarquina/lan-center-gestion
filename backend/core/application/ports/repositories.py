"""Puertos (interfaces) de repositorios de la capa de aplicación.

Define contratos que los adaptadores de infraestructura deben implementar para
persistir y recuperar entidades de dominio. Mantiene la capa de aplicación
independiente de detalles tecnológicos (ORM, base de datos, APIs externas).

Este puerto cubre operaciones necesarias para casos de uso relacionados con
cabinas (CU03) y requisitos funcionales RF06–RF10.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from backend.core.domain.models.cabina import Cabina, EstadoCabina


class CabinaRepositoryPort(ABC):
	"""Contrato para operaciones de persistencia de Cabina.

	Métodos mínimos para soporte de casos de uso actuales:
	 - guardar: crear o actualizar cabina
	 - obtener_por_id: recuperar por identificador interno
	 - buscar_por_numero: recuperar por número operativo único
	 - buscar_por_estado: listar cabinas en un estado específico
	 - listar_todas: listado completo (para panel de control)
	 - eliminar: baja lógica/física (según implementación) respetando reglas
	"""

	@abstractmethod
	def guardar(self, cabina: Cabina) -> Cabina:
		"""Persiste la cabina (insert/update) y retorna instancia actualizada."""
		raise NotImplementedError

	@abstractmethod
	def obtener_por_id(self, cabina_id: int) -> Optional[Cabina]:
		"""Obtiene una cabina por su ID interno."""
		raise NotImplementedError

	@abstractmethod
	def buscar_por_numero(self, numero: int) -> Optional[Cabina]:
		"""Busca una cabina por su número operativo único."""
		raise NotImplementedError

	@abstractmethod
	def buscar_por_estado(self, estado: EstadoCabina) -> List[Cabina]:
		"""Lista cabinas filtradas por estado."""
		raise NotImplementedError

	@abstractmethod
	def listar_todas(self) -> List[Cabina]:
		"""Retorna todas las cabinas disponibles en el sistema."""
		raise NotImplementedError

	@abstractmethod
	def eliminar(self, cabina_id: int) -> None:
		"""Elimina (o da de baja) una cabina.

		La política de eliminación (física vs lógica) queda a cargo del adapter.
		Debe impedir eliminar cabinas en estado OCUPADA (RF09).
		"""
		raise NotImplementedError

