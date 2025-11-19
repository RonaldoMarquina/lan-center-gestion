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


