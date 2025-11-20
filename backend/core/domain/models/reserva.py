"""Entidad de dominio Reserva."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class EstadoReserva(Enum):
    """Estados posibles de una reserva."""
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    EN_CURSO = "en_curso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"


@dataclass
class Reserva:
    """Representa una reserva de cabina."""
    
    id: Optional[int]
    usuario_id: int
    cabina_id: int
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    estado: EstadoReserva
    creada_en: datetime
    
    def __post_init__(self):
        """Valida invariantes del dominio."""
        if self.fecha_hora_fin <= self.fecha_hora_inicio:
            raise ValueError("La fecha de fin debe ser posterior a la de inicio")
        
        if self.estado not in EstadoReserva:
            raise ValueError(f"Estado inválido: {self.estado}")
    
    def confirmar(self):
        """Confirma una reserva pendiente."""
        if self.estado != EstadoReserva.PENDIENTE:
            raise ValueError("Solo se pueden confirmar reservas pendientes")
        self.estado = EstadoReserva.CONFIRMADA
    
    def iniciar(self):
        """Inicia una reserva confirmada."""
        if self.estado != EstadoReserva.CONFIRMADA:
            raise ValueError("Solo se pueden iniciar reservas confirmadas")
        self.estado = EstadoReserva.EN_CURSO
    
    def completar(self):
        """Completa una reserva en curso."""
        if self.estado != EstadoReserva.EN_CURSO:
            raise ValueError("Solo se pueden completar reservas en curso")
        self.estado = EstadoReserva.COMPLETADA
    
    def cancelar(self):
        """Cancela una reserva pendiente o confirmada."""
        if self.estado not in [EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA]:
            raise ValueError("Solo se pueden cancelar reservas pendientes o confirmadas")
        self.estado = EstadoReserva.CANCELADA
    
    def duracion_minutos(self) -> int:
        """Calcula duración de la reserva en minutos."""
        delta = self.fecha_hora_fin - self.fecha_hora_inicio
        return int(delta.total_seconds() / 60)
    
    def tiene_conflicto(self, otra_reserva: 'Reserva') -> bool:
        """Verifica si hay conflicto de horario con otra reserva."""
        if self.cabina_id != otra_reserva.cabina_id:
            return False
        
        # Verificar solapamiento de rangos
        return (
            self.fecha_hora_inicio < otra_reserva.fecha_hora_fin and
            self.fecha_hora_fin > otra_reserva.fecha_hora_inicio
        )

