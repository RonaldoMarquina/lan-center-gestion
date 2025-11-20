"""Modelos de persistencia (Django ORM)."""

from django.db import models
from django.contrib.auth.models import User

from core.domain.models.cabina import TipoCabina, EstadoCabina, Cabina
from core.domain.models.reserva import EstadoReserva, Reserva
from core.domain.models.sesion import EstadoSesion, Sesion
from decimal import Decimal


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


class ReservaModel(models.Model):
	"""Modelo Django para Reserva."""

	usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas')
	cabina = models.ForeignKey(CabinaModel, on_delete=models.CASCADE, related_name='reservas')
	fecha_hora_inicio = models.DateTimeField()
	fecha_hora_fin = models.DateTimeField()
	estado = models.CharField(
		max_length=16,
		choices=[(e.value, e.value) for e in EstadoReserva],
		default=EstadoReserva.PENDIENTE.value,
	)
	creada_en = models.DateTimeField(auto_now_add=True)
	actualizado_en = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = "reservas"
		ordering = ["-creada_en"]
		indexes = [
			models.Index(fields=['cabina', 'fecha_hora_inicio', 'fecha_hora_fin']),
			models.Index(fields=['usuario', 'estado']),
		]

	def __str__(self) -> str:  # pragma: no cover
		return f"Reserva {self.id} - Cabina {self.cabina.numero}"

	def to_domain(self) -> Reserva:
		return Reserva(
			id=self.id,
			usuario_id=self.usuario_id,
			cabina_id=self.cabina_id,
			fecha_hora_inicio=self.fecha_hora_inicio,
			fecha_hora_fin=self.fecha_hora_fin,
			estado=EstadoReserva[self.estado.upper()],
			creada_en=self.creada_en,
		)

	@staticmethod
	def from_domain(reserva: Reserva) -> "ReservaModel":
		instance = ReservaModel(
			id=reserva.id,
			usuario_id=reserva.usuario_id,
			cabina_id=reserva.cabina_id,
			fecha_hora_inicio=reserva.fecha_hora_inicio,
			fecha_hora_fin=reserva.fecha_hora_fin,
			estado=reserva.estado.value,
		)
		# Preservar creada_en si existe
		if hasattr(reserva, 'creada_en') and reserva.creada_en:
			instance.creada_en = reserva.creada_en
		return instance


class SesionModel(models.Model):
	"""Modelo Django para Sesion."""

	reserva = models.OneToOneField(ReservaModel, on_delete=models.CASCADE, related_name='sesion')
	cabina = models.ForeignKey(CabinaModel, on_delete=models.CASCADE, related_name='sesiones')
	usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sesiones')
	fecha_hora_inicio = models.DateTimeField()
	fecha_hora_fin = models.DateTimeField(null=True, blank=True)
	tiempo_total_minutos = models.PositiveIntegerField(default=0)
	costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	precio_por_hora = models.DecimalField(max_digits=8, decimal_places=2)
	estado = models.CharField(
		max_length=16,
		choices=[(e.value, e.value) for e in EstadoSesion],
		default=EstadoSesion.ACTIVA.value,
	)
	creado_en = models.DateTimeField(auto_now_add=True)
	actualizado_en = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = "sesiones"
		ordering = ["-creado_en"]
		indexes = [
			models.Index(fields=['usuario', 'estado']),
			models.Index(fields=['cabina', 'estado']),
		]

	def __str__(self) -> str:  # pragma: no cover
		return f"Sesion {self.id} - Cabina {self.cabina.numero}"

	def to_domain(self) -> Sesion:
		return Sesion(
			id=self.id,
			reserva_id=self.reserva_id,
			cabina_id=self.cabina_id,
			usuario_id=self.usuario_id,
			fecha_hora_inicio=self.fecha_hora_inicio,
			fecha_hora_fin=self.fecha_hora_fin,
			tiempo_total_minutos=self.tiempo_total_minutos,
			costo_total=Decimal(str(self.costo_total)),
			precio_por_hora=Decimal(str(self.precio_por_hora)),
			estado=EstadoSesion[self.estado.upper()],
		)

	@staticmethod
	def from_domain(sesion: Sesion) -> "SesionModel":
		instance = SesionModel(
			id=sesion.id,
			reserva_id=sesion.reserva_id,
			cabina_id=sesion.cabina_id,
			usuario_id=sesion.usuario_id,
			fecha_hora_inicio=sesion.fecha_hora_inicio,
			fecha_hora_fin=sesion.fecha_hora_fin,
			tiempo_total_minutos=sesion.tiempo_total_minutos,
			costo_total=sesion.costo_total,
			precio_por_hora=sesion.precio_por_hora,
			estado=sesion.estado.value,
		)
		return instance


class PagoModel(models.Model):
	"""Modelo Django para Pago."""

	METODO_PAGO_CHOICES = [
		("efectivo", "Efectivo"),
		("tarjeta", "Tarjeta"),
		("transferencia", "Transferencia"),
		("billetera_digital", "Billetera Digital"),
	]

	ESTADO_CHOICES = [
		("pendiente", "Pendiente"),
		("completado", "Completado"),
		("fallido", "Fallido"),
		("reembolsado", "Reembolsado"),
	]

	sesion = models.OneToOneField(
		SesionModel, on_delete=models.CASCADE, related_name="pago"
	)
	usuario = models.ForeignKey(User, on_delete=models.CASCADE)
	monto = models.DecimalField(max_digits=10, decimal_places=2)
	metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
	estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="pendiente")
	fecha_pago = models.DateTimeField()
	comprobante_numero = models.CharField(max_length=50, null=True, blank=True, unique=True)
	notas = models.TextField(blank=True, default="")

	class Meta:
		db_table = "pagos"
		ordering = ["-fecha_pago"]
		indexes = [
			models.Index(fields=["usuario", "estado"]),
			models.Index(fields=["fecha_pago"]),
			models.Index(fields=["comprobante_numero"]),
		]

	def to_domain(self) -> "Pago":
		"""Convertir a entidad dominio."""
		from core.domain.models.pago import Pago, MetodoPago, EstadoPago

		return Pago(
			id=self.id,
			sesion_id=self.sesion_id,
			usuario_id=self.usuario_id,
			monto=self.monto,
			metodo_pago=MetodoPago[self.metodo_pago.upper()],
			estado=EstadoPago[self.estado.upper()],
			fecha_pago=self.fecha_pago,
			comprobante_numero=self.comprobante_numero,
			notas=self.notas,
		)

	@staticmethod
	def from_domain(pago: "Pago") -> "PagoModel":
		"""Crear desde entidad dominio."""
		return PagoModel(
			id=pago.id if pago.id != 0 else None,
			sesion_id=pago.sesion_id,
			usuario_id=pago.usuario_id,
			monto=pago.monto,
			metodo_pago=pago.metodo_pago.value.lower(),
			estado=pago.estado.value.lower(),
			fecha_pago=pago.fecha_pago,
			comprobante_numero=pago.comprobante_numero,
			notas=pago.notas,
		)
