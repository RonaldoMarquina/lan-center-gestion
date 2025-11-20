"""Casos de uso para gestionar Reservas."""
from datetime import datetime
from typing import List, Optional

from core.domain.models.reserva import Reserva, EstadoReserva
from core.domain.models.cabina import EstadoCabina
from core.application.ports.repositories import ReservaRepositoryPort, CabinaRepositoryPort


class GestionarReservas:
    """Casos de uso de Reserva."""
    
    def __init__(
        self,
        reserva_repository: ReservaRepositoryPort,
        cabina_repository: CabinaRepositoryPort
    ):
        self.reserva_repo = reserva_repository
        self.cabina_repo = cabina_repository
    
    def crear_reserva(
        self,
        usuario_id: int,
        cabina_id: int,
        fecha_hora_inicio: datetime,
        fecha_hora_fin: datetime
    ) -> Reserva:
        """Crea una nueva reserva."""
        # Validar que la cabina existe y está disponible
        cabina = self.cabina_repo.obtener_por_id(cabina_id)
        if not cabina:
            raise ValueError(f"Cabina con id {cabina_id} no existe")
        
        if cabina.estado not in [EstadoCabina.DISPONIBLE, EstadoCabina.OCUPADA]:
            raise ValueError(f"Cabina en estado {cabina.estado.value} no puede reservarse")
        
        # Verificar conflictos de horario
        conflictos = self.reserva_repo.buscar_conflictos(
            cabina_id,
            fecha_hora_inicio,
            fecha_hora_fin
        )
        if conflictos:
            raise ValueError("Conflicto de horario: ya existe una reserva en ese horario")
        
        # Crear reserva
        reserva = Reserva(
            id=None,
            usuario_id=usuario_id,
            cabina_id=cabina_id,
            fecha_hora_inicio=fecha_hora_inicio,
            fecha_hora_fin=fecha_hora_fin,
            estado=EstadoReserva.PENDIENTE,
            creada_en=datetime.now()
        )
        
        return self.reserva_repo.guardar(reserva)
    
    def confirmar_reserva(self, reserva_id: int) -> Reserva:
        """Confirma una reserva pendiente."""
        reserva = self.reserva_repo.obtener_por_id(reserva_id)
        if not reserva:
            raise ValueError(f"Reserva con id {reserva_id} no existe")
        
        reserva.confirmar()
        return self.reserva_repo.guardar(reserva)
    
    def iniciar_reserva(self, reserva_id: int) -> Reserva:
        """Inicia una reserva confirmada."""
        reserva = self.reserva_repo.obtener_por_id(reserva_id)
        if not reserva:
            raise ValueError(f"Reserva con id {reserva_id} no existe")
        
        reserva.iniciar()
        
        # Cambiar estado de cabina a OCUPADA
        cabina = self.cabina_repo.obtener_por_id(reserva.cabina_id)
        if cabina:
            cabina.ocupar()
            self.cabina_repo.guardar(cabina)
        
        return self.reserva_repo.guardar(reserva)
    
    def cancelar_reserva(self, reserva_id: int) -> Reserva:
        """Cancela una reserva."""
        reserva = self.reserva_repo.obtener_por_id(reserva_id)
        if not reserva:
            raise ValueError(f"Reserva con id {reserva_id} no existe")
        
        reserva.cancelar()
        return self.reserva_repo.guardar(reserva)
    
    def obtener_reserva(self, reserva_id: int) -> Optional[Reserva]:
        """Obtiene una reserva por id."""
        return self.reserva_repo.obtener_por_id(reserva_id)
    
    def listar_reservas_usuario(self, usuario_id: int) -> List[Reserva]:
        """Lista reservas de un usuario."""
        return self.reserva_repo.listar_por_usuario(usuario_id)
    
    def listar_reservas_cabina(self, cabina_id: int) -> List[Reserva]:
        """Lista reservas de una cabina."""
        return self.reserva_repo.listar_por_cabina(cabina_id)
    
    def listar_reservas_activas(self) -> List[Reserva]:
        """Lista reservas activas (pendientes, confirmadas y en curso)."""
        pendientes = self.reserva_repo.listar_por_estado(EstadoReserva.PENDIENTE)
        confirmadas = self.reserva_repo.listar_por_estado(EstadoReserva.CONFIRMADA)
        en_curso = self.reserva_repo.listar_por_estado(EstadoReserva.EN_CURSO)
        return pendientes + confirmadas + en_curso
