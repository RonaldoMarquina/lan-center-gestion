"""Modelos de persistencia (Django ORM)."""

from django.db import models

from core.domain.models.cabina import TipoCabina, EstadoCabina, Cabina


class CabinaModel(models.Model):
	"""Modelo Django para Cabina."""

	numero = models.PositiveIntegerField(unique=True)
	tipo = models.CharField(
		max_length=16,
		choices=[(t.value, t.value) for t in TipoCabina],
	)
	estado = models.CharField(
		max_length=16,
		choices=[(e.value, e.value) for e in EstadoCabina],
		default=EstadoCabina.DISPONIBLE.value,
	)
	especificaciones = models.JSONField(default=dict, blank=True)
	precio_por_hora = models.DecimalField(max_digits=8, decimal_places=2)
	creado_en = models.DateTimeField(auto_now_add=True)
	actualizado_en = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = "cabinas"
		ordering = ["numero"]

	def __str__(self) -> str:  # pragma: no cover
		return f"Cabina {self.numero} ({self.tipo})"

	# Mapping helpers -----------------
	def to_domain(self) -> Cabina:
		return Cabina(
			id=self.id,
			numero=self.numero,
			tipo=TipoCabina[self.tipo],
			estado=EstadoCabina[self.estado],
			especificaciones=self.especificaciones or {},
			precio_por_hora=float(self.precio_por_hora),
		)

	@staticmethod
	def from_domain(cabina: Cabina) -> "CabinaModel":
		instance = CabinaModel(
			id=cabina.id,
			numero=cabina.numero,
			tipo=cabina.tipo.value,
			estado=cabina.estado.value,
			especificaciones=cabina.especificaciones,
			precio_por_hora=cabina.precio_por_hora,
		)
		return instance

