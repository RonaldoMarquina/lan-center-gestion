"""Views Cabina (ViewSet)."""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.utils import IntegrityError

from core.application.use_cases.gestionar_cabinas import GestionarCabinas
from infrastructure.persistence.repositories import DjangoCabinaRepository
from core.domain.models.cabina import EstadoCabina
from .serializers import (
	CabinaSerializer,
	CabinaCreateSerializer,
	CabinaPrecioSerializer,
)


class CabinaViewSet(viewsets.ViewSet):
	"""Operaciones CRUD y estado de cabinas."""

	repo = DjangoCabinaRepository()
	use_case = GestionarCabinas(repo)

	def list(self, request):
		cabinas = self.use_case.listar_todas_cabinas()
		ser = CabinaSerializer(cabinas, many=True)
		return Response(ser.data)

	@action(detail=False, methods=["get"], url_path="disponibles")
	def disponibles(self, request):
		cabinas = self.use_case.listar_cabinas_disponibles()
		ser = CabinaSerializer(cabinas, many=True)
		return Response(ser.data)

	def create(self, request):
		ser = CabinaCreateSerializer(data=request.data)
		ser.is_valid(raise_exception=True)
		data = ser.validated_data
		try:
			cabina = self.use_case.crear_cabina(
				numero=data["numero"],
				tipo=data["tipo"],
				especificaciones=data.get("especificaciones", {}),
				precio_por_hora=data["precio_por_hora"],
			)
			return Response(CabinaSerializer(cabina).data, status=status.HTTP_201_CREATED)
		except ValueError as ex:
			return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
		except IntegrityError:
			return Response({"detail": "El número de cabina ya existe"}, status=status.HTTP_400_BAD_REQUEST)

	def destroy(self, request, pk=None):
		cabina = self.use_case.obtener_cabina(int(pk))
		if not cabina:
			return Response({"detail": "No encontrada"}, status=status.HTTP_404_NOT_FOUND)
		try:
			self.repo.eliminar(cabina.id)
			return Response(status=status.HTTP_204_NO_CONTENT)
		except ValueError as ex:
			return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=True, methods=["post"], url_path="ocupar")
	def ocupar(self, request, pk=None):
		if not self.use_case.obtener_cabina(int(pk)):
			return Response({"detail": "No encontrada"}, status=status.HTTP_404_NOT_FOUND)
		try:
			cabina = self.use_case.ocupar_cabina(int(pk))
			return Response(CabinaSerializer(cabina).data)
		except ValueError as ex:
			return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=True, methods=["post"], url_path="liberar")
	def liberar(self, request, pk=None):
		if not self.use_case.obtener_cabina(int(pk)):
			return Response({"detail": "No encontrada"}, status=status.HTTP_404_NOT_FOUND)
		try:
			cabina = self.use_case.liberar_cabina(int(pk))
			return Response(CabinaSerializer(cabina).data)
		except ValueError as ex:
			return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=True, methods=["post"], url_path="mantenimiento/iniciar")
	def iniciar_mantenimiento(self, request, pk=None):
		if not self.use_case.obtener_cabina(int(pk)):
			return Response({"detail": "No encontrada"}, status=status.HTTP_404_NOT_FOUND)
		try:
			cabina = self.use_case.iniciar_mantenimiento(int(pk))
			return Response(CabinaSerializer(cabina).data)
		except ValueError as ex:
			return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=True, methods=["post"], url_path="mantenimiento/finalizar")
	def finalizar_mantenimiento(self, request, pk=None):
		if not self.use_case.obtener_cabina(int(pk)):
			return Response({"detail": "No encontrada"}, status=status.HTTP_404_NOT_FOUND)
		try:
			cabina = self.use_case.finalizar_mantenimiento(int(pk))
			return Response(CabinaSerializer(cabina).data)
		except ValueError as ex:
			return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=True, methods=["patch"], url_path="precio")
	def actualizar_precio(self, request, pk=None):
		ser = CabinaPrecioSerializer(data=request.data)
		ser.is_valid(raise_exception=True)
		if not self.use_case.obtener_cabina(int(pk)):
			return Response({"detail": "No encontrada"}, status=status.HTTP_404_NOT_FOUND)
		try:
			cabina = self.use_case.actualizar_precio(int(pk), ser.validated_data["precio_por_hora"])
			return Response(CabinaSerializer(cabina).data)
		except ValueError as ex:
			return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)


