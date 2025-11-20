"""Serializers para cabinas."""

from rest_framework import serializers

from core.domain.models.cabina import TipoCabina


class CabinaSerializer(serializers.Serializer):
	id = serializers.IntegerField(read_only=True)
	numero = serializers.IntegerField()
	tipo = serializers.CharField()
	estado = serializers.CharField(read_only=True)
	especificaciones = serializers.JSONField()
	precio_por_hora = serializers.FloatField()

	def to_representation(self, instance):  # instance: domain Cabina
		return instance.to_dict()


class CabinaCreateSerializer(serializers.Serializer):
	numero = serializers.IntegerField(min_value=1)
	tipo = serializers.ChoiceField(choices=[t.name.lower() for t in TipoCabina])
	especificaciones = serializers.JSONField(required=False, default=dict)
	precio_por_hora = serializers.FloatField(min_value=0.01)


class CabinaPrecioSerializer(serializers.Serializer):
	precio_por_hora = serializers.FloatField(min_value=0.01)


# Serializers para Reservas

class ReservaSerializer(serializers.Serializer):
	id = serializers.IntegerField(read_only=True)
	usuario_id = serializers.IntegerField()
	cabina_id = serializers.IntegerField()
	fecha_hora_inicio = serializers.DateTimeField()
	fecha_hora_fin = serializers.DateTimeField()
	estado = serializers.CharField(read_only=True)
	creada_en = serializers.DateTimeField(read_only=True)
	
	def to_representation(self, instance):
		"""Convertir enums a sus valores."""
		return {
			'id': instance.id,
			'usuario_id': instance.usuario_id,
			'cabina_id': instance.cabina_id,
			'fecha_hora_inicio': instance.fecha_hora_inicio.isoformat(),
			'fecha_hora_fin': instance.fecha_hora_fin.isoformat(),
			'estado': instance.estado.value,
			'creada_en': instance.creada_en.isoformat(),
		}


class ReservaCreateSerializer(serializers.Serializer):
	usuario_id = serializers.IntegerField(min_value=1)
	cabina_id = serializers.IntegerField(min_value=1)
	fecha_hora_inicio = serializers.DateTimeField()
	fecha_hora_fin = serializers.DateTimeField()


# Serializers para Sesiones

class SesionSerializer(serializers.Serializer):
	id = serializers.IntegerField(read_only=True)
	reserva_id = serializers.IntegerField()
	cabina_id = serializers.IntegerField()
	usuario_id = serializers.IntegerField()
	fecha_hora_inicio = serializers.DateTimeField()
	fecha_hora_fin = serializers.DateTimeField(allow_null=True)
	tiempo_total_minutos = serializers.IntegerField()
	costo_total = serializers.DecimalField(max_digits=10, decimal_places=2)
	precio_por_hora = serializers.DecimalField(max_digits=8, decimal_places=2)
	estado = serializers.CharField(read_only=True)
	
	def to_representation(self, instance):
		"""Convertir enums a sus valores."""
		return {
			'id': instance.id,
			'reserva_id': instance.reserva_id,
			'cabina_id': instance.cabina_id,
			'usuario_id': instance.usuario_id,
			'fecha_hora_inicio': instance.fecha_hora_inicio.isoformat(),
			'fecha_hora_fin': instance.fecha_hora_fin.isoformat() if instance.fecha_hora_fin else None,
			'tiempo_total_minutos': instance.tiempo_total_minutos,
			'costo_total': str(instance.costo_total),
			'precio_por_hora': str(instance.precio_por_hora),
			'estado': instance.estado.value,
		}


class SesionExtenderSerializer(serializers.Serializer):
	minutos_adicionales = serializers.IntegerField(min_value=1)
