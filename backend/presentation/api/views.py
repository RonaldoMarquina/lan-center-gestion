"""Views Cabina, Reserva y Sesion (ViewSets)."""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.utils import IntegrityError

from core.application.use_cases.gestionar_cabinas import GestionarCabinas
from core.application.use_cases.gestionar_reservas import GestionarReservas
from core.application.use_cases.gestionar_sesiones import GestionarSesiones
from infrastructure.persistence.repositories import (
	DjangoCabinaRepository,
	DjangoReservaRepository,
	DjangoSesionRepository,
)
from core.domain.models.cabina import EstadoCabina
from .serializers import (
	CabinaSerializer,
	CabinaCreateSerializer,
	CabinaPrecioSerializer,
	ReservaSerializer,
	ReservaCreateSerializer,
	SesionSerializer,
	SesionExtenderSerializer,
)


class CabinaViewSet(viewsets.ViewSet):
	"""Operaciones CRUD y estado de cabinas."""

	repo = DjangoCabinaRepository()
	use_case = GestionarCabinas(repo)

	def list(self, request):
		cabinas = self.use_case.listar_todas_cabinas()
		ser = CabinaSerializer(cabinas, many=True)
		return Response(ser.data)

	def retrieve(self, request, pk=None):
		"""Obtiene una cabina por id."""
		cabina = self.use_case.obtener_cabina(int(pk))
		if not cabina:
			return Response({"detail": "No encontrada"}, status=status.HTTP_404_NOT_FOUND)
		return Response(CabinaSerializer(cabina).data)

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


class ReservaViewSet(viewsets.ViewSet):
	"""Operaciones CRUD de Reservas."""

	reserva_repo = DjangoReservaRepository()
	cabina_repo = DjangoCabinaRepository()
	use_case = GestionarReservas(reserva_repo, cabina_repo)

	def list(self, request):
		"""Lista todas las reservas."""
		usuario_id = request.query_params.get('usuario_id')
		cabina_id = request.query_params.get('cabina_id')
		
		if usuario_id:
			reservas = self.use_case.listar_reservas_usuario(int(usuario_id))
		elif cabina_id:
			reservas = self.use_case.listar_reservas_cabina(int(cabina_id))
		else:
			reservas = self.use_case.listar_reservas_activas()
		
		ser = ReservaSerializer(reservas, many=True)
		return Response(ser.data)

	def retrieve(self, request, pk=None):
		"""Obtiene una reserva por id."""
		reserva = self.use_case.obtener_reserva(int(pk))
		if not reserva:
			return Response({"detail": "No encontrada"}, status=status.HTTP_404_NOT_FOUND)
		return Response(ReservaSerializer(reserva).data)

	def create(self, request):
		"""Crea una nueva reserva."""
		ser = ReservaCreateSerializer(data=request.data)
		ser.is_valid(raise_exception=True)
		data = ser.validated_data
		
		try:
			reserva = self.use_case.crear_reserva(
				usuario_id=data["usuario_id"],
				cabina_id=data["cabina_id"],
				fecha_hora_inicio=data["fecha_hora_inicio"],
				fecha_hora_fin=data["fecha_hora_fin"],
			)
			return Response(ReservaSerializer(reserva).data, status=status.HTTP_201_CREATED)
		except ValueError as ex:
			return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=True, methods=["post"], url_path="confirmar")
	def confirmar(self, request, pk=None):
		"""Confirma una reserva pendiente."""
		try:
			reserva = self.use_case.confirmar_reserva(int(pk))
			return Response(ReservaSerializer(reserva).data)
		except ValueError as ex:
			return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=True, methods=["post"], url_path="iniciar")
	def iniciar(self, request, pk=None):
		"""Inicia una reserva confirmada."""
		try:
			reserva = self.use_case.iniciar_reserva(int(pk))
			return Response(ReservaSerializer(reserva).data)
		except ValueError as ex:
			return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=True, methods=["post"], url_path="cancelar")
	def cancelar(self, request, pk=None):
		"""Cancela una reserva."""
		try:
			reserva = self.use_case.cancelar_reserva(int(pk))
			return Response(ReservaSerializer(reserva).data)
		except ValueError as ex:
			return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)


class SesionViewSet(viewsets.ViewSet):
	"""Operaciones de Sesiones de uso."""

	sesion_repo = DjangoSesionRepository()
	reserva_repo = DjangoReservaRepository()
	cabina_repo = DjangoCabinaRepository()
	use_case = GestionarSesiones(sesion_repo, reserva_repo, cabina_repo)

	def list(self, request):
		"""Lista sesiones (todas o filtradas)."""
		usuario_id = request.query_params.get('usuario_id')
		activas = request.query_params.get('activas')
		
		if activas == 'true':
			sesiones = self.use_case.listar_sesiones_activas()
		elif usuario_id:
			sesiones = self.use_case.listar_sesiones_usuario(int(usuario_id))
		else:
			sesiones = self.use_case.listar_sesiones_activas()
		
		ser = SesionSerializer(sesiones, many=True)
		return Response(ser.data)

	def retrieve(self, request, pk=None):
		"""Obtiene una sesión por id."""
		sesion = self.use_case.obtener_sesion(int(pk))
		if not sesion:
			return Response({"detail": "No encontrada"}, status=status.HTTP_404_NOT_FOUND)
		return Response(SesionSerializer(sesion).data)

	def create(self, request):
		"""Inicia una sesión desde una reserva."""
		reserva_id = request.data.get('reserva_id')
		if not reserva_id:
			return Response({"detail": "reserva_id requerido"}, status=status.HTTP_400_BAD_REQUEST)
		
		try:
			sesion = self.use_case.iniciar_sesion(int(reserva_id))
			return Response(SesionSerializer(sesion).data, status=status.HTTP_201_CREATED)
		except ValueError as ex:
			return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=True, methods=["post"], url_path="finalizar")
	def finalizar(self, request, pk=None):
		"""Finaliza una sesión activa."""
		try:
			sesion = self.use_case.finalizar_sesion(int(pk))
			return Response(SesionSerializer(sesion).data)
		except ValueError as ex:
			return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=True, methods=["post"], url_path="extender")
	def extender(self, request, pk=None):
		"""Extiende una sesión activa."""
		ser = SesionExtenderSerializer(data=request.data)
		ser.is_valid(raise_exception=True)
		
		try:
			sesion = self.use_case.extender_sesion(int(pk), ser.validated_data["minutos_adicionales"])
			return Response(SesionSerializer(sesion).data)
		except ValueError as ex:
			return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=True, methods=["post"], url_path="pausar")
	def pausar(self, request, pk=None):
		"""Pausa una sesión activa."""
		try:
			sesion = self.use_case.pausar_sesion(int(pk))
			return Response(SesionSerializer(sesion).data)
		except ValueError as ex:
			return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=True, methods=["post"], url_path="reanudar")
	def reanudar(self, request, pk=None):
		"""Reanuda una sesión pausada."""
		try:
			sesion = self.use_case.reanudar_sesion(int(pk))
			return Response(SesionSerializer(sesion).data)
		except ValueError as ex:
			return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=True, methods=["post"], url_path="cancelar")
	def cancelar(self, request, pk=None):
		"""Cancela una sesión."""
		try:
			sesion = self.use_case.cancelar_sesion(int(pk))
			return Response(SesionSerializer(sesion).data)
		except ValueError as ex:
			return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=True, methods=["get"], url_path="costo-actual")
	def costo_actual(self, request, pk=None):
		"""Calcula el costo actual de una sesión."""
		try:
			costo = self.use_case.calcular_costo_actual(int(pk))
			return Response({"costo_actual": str(costo)})
		except ValueError as ex:
			return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
