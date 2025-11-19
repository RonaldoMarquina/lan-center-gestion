"""Adapter repositorio Cabina (Django ORM)."""

from typing import List, Optional

from django.db import transaction

from core.application.ports.repositories import CabinaRepositoryPort
from core.domain.models.cabina import Cabina, EstadoCabina
from .models import CabinaModel


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

