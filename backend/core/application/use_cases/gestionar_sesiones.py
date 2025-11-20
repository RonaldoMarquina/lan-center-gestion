"""Casos de uso para gestionar Sesiones."""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from django.utils import timezone

from core.domain.models.sesion import Sesion, EstadoSesion
from core.domain.models.reserva import EstadoReserva
from core.domain.models.cabina import EstadoCabina
from core.application.ports.repositories import (
    SesionRepositoryPort,
    ReservaRepositoryPort,
    CabinaRepositoryPort
)


class GestionarSesiones:
    """Casos de uso de Sesion."""
    
    def __init__(
        self,
        sesion_repository: SesionRepositoryPort,
        reserva_repository: ReservaRepositoryPort,
        cabina_repository: CabinaRepositoryPort
    ):
        self.sesion_repo = sesion_repository
        self.reserva_repo = reserva_repository
        self.cabina_repo = cabina_repository
    
    def iniciar_sesion(self, reserva_id: int) -> Sesion:
        """Inicia una sesión desde una reserva."""
        # Validar que la reserva existe y está confirmada
        reserva = self.reserva_repo.obtener_por_id(reserva_id)
        if not reserva:
            raise ValueError(f"Reserva con id {reserva_id} no existe")
        
        if reserva.estado != EstadoReserva.CONFIRMADA:
            raise ValueError("Solo se pueden iniciar sesiones de reservas confirmadas")
        
        # Verificar que no existe una sesión activa para esta reserva
        sesion_existente = self.sesion_repo.obtener_por_reserva(reserva_id)
        if sesion_existente and sesion_existente.estado == EstadoSesion.ACTIVA:
            raise ValueError("Ya existe una sesión activa para esta reserva")
        
        # Obtener precio de la cabina
        cabina = self.cabina_repo.obtener_por_id(reserva.cabina_id)
        if not cabina:
            raise ValueError(f"Cabina con id {reserva.cabina_id} no existe")
        
        # Crear sesión
        sesion = Sesion(
            id=None,
            reserva_id=reserva_id,
            cabina_id=reserva.cabina_id,
            usuario_id=reserva.usuario_id,
            fecha_hora_inicio=timezone.now(),
            fecha_hora_fin=None,
            tiempo_total_minutos=0,
            costo_total=Decimal('0.00'),
            precio_por_hora=Decimal(str(cabina.precio_por_hora)),
            estado=EstadoSesion.ACTIVA
        )
        
        # Marcar reserva como en curso
        reserva.iniciar()
        self.reserva_repo.guardar(reserva)
        
        # Marcar cabina como ocupada
        cabina.ocupar()
        self.cabina_repo.guardar(cabina)
        
        return self.sesion_repo.guardar(sesion)
    
    def finalizar_sesion(self, sesion_id: int) -> Sesion:
        """Finaliza una sesión activa."""
        sesion = self.sesion_repo.obtener_por_id(sesion_id)
        if not sesion:
            raise ValueError(f"Sesión con id {sesion_id} no existe")
        
        # Finalizar sesión (calcula tiempo y costo)
        sesion.finalizar(timezone.now())
        sesion_actualizada = self.sesion_repo.guardar(sesion)
        
        # Completar reserva
        reserva = self.reserva_repo.obtener_por_id(sesion.reserva_id)
        if reserva:
            reserva.completar()
            self.reserva_repo.guardar(reserva)
        
        # Liberar cabina
        cabina = self.cabina_repo.obtener_por_id(sesion.cabina_id)
        if cabina:
            cabina.liberar()
            self.cabina_repo.guardar(cabina)
        
        return sesion_actualizada
    
    def extender_sesion(self, sesion_id: int, minutos_adicionales: int) -> Sesion:
        """Extiende una sesión activa."""
        sesion = self.sesion_repo.obtener_por_id(sesion_id)
        if not sesion:
            raise ValueError(f"Sesión con id {sesion_id} no existe")
        
        sesion.extender(minutos_adicionales)
        return self.sesion_repo.guardar(sesion)
    
    def pausar_sesion(self, sesion_id: int) -> Sesion:
        """Pausa una sesión activa."""
        sesion = self.sesion_repo.obtener_por_id(sesion_id)
        if not sesion:
            raise ValueError(f"Sesión con id {sesion_id} no existe")
        
        sesion.pausar()
        return self.sesion_repo.guardar(sesion)
    
    def reanudar_sesion(self, sesion_id: int) -> Sesion:
        """Reanuda una sesión pausada."""
        sesion = self.sesion_repo.obtener_por_id(sesion_id)
        if not sesion:
            raise ValueError(f"Sesión con id {sesion_id} no existe")
        
        sesion.reanudar()
        return self.sesion_repo.guardar(sesion)
    
    def cancelar_sesion(self, sesion_id: int) -> Sesion:
        """Cancela una sesión activa."""
        sesion = self.sesion_repo.obtener_por_id(sesion_id)
        if not sesion:
            raise ValueError(f"Sesión con id {sesion_id} no existe")
        
        sesion.cancelar()
        sesion_actualizada = self.sesion_repo.guardar(sesion)
        
        # Liberar cabina
        cabina = self.cabina_repo.obtener_por_id(sesion.cabina_id)
        if cabina:
            cabina.liberar()
            self.cabina_repo.guardar(cabina)
        
        return sesion_actualizada
    
    def obtener_sesion(self, sesion_id: int) -> Optional[Sesion]:
        """Obtiene una sesión por id."""
        return self.sesion_repo.obtener_por_id(sesion_id)
    
    def listar_sesiones_usuario(self, usuario_id: int) -> List[Sesion]:
        """Lista sesiones de un usuario."""
        return self.sesion_repo.listar_por_usuario(usuario_id)
    
    def listar_sesiones_activas(self) -> List[Sesion]:
        """Lista todas las sesiones activas."""
        return self.sesion_repo.listar_activas()
    
    def calcular_costo_actual(self, sesion_id: int) -> Decimal:
        """Calcula costo actual de una sesión en tiempo real."""
        sesion = self.sesion_repo.obtener_por_id(sesion_id)
        if not sesion:
            raise ValueError(f"Sesión con id {sesion_id} no existe")
        
        return sesion.calcular_costo_actual()
