"""Entidad de dominio Sesion."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from django.utils import timezone


class EstadoSesion(Enum):
    """Estados posibles de una sesión de uso."""
    ACTIVA = "activa"
    PAUSADA = "pausada"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"


@dataclass
class Sesion:
    """Representa una sesión de uso de cabina."""
    
    id: Optional[int]
    reserva_id: int
    cabina_id: int
    usuario_id: int
    fecha_hora_inicio: datetime
    fecha_hora_fin: Optional[datetime]
    tiempo_total_minutos: int
    costo_total: Decimal
    precio_por_hora: Decimal
    estado: EstadoSesion
    
    def __post_init__(self):
        """Valida invariantes del dominio."""
        if self.precio_por_hora <= 0:
            raise ValueError("El precio por hora debe ser positivo")
        
        if self.fecha_hora_fin and self.fecha_hora_fin < self.fecha_hora_inicio:
            raise ValueError("La fecha de fin no puede ser anterior al inicio")
        
        if self.estado not in EstadoSesion:
            raise ValueError(f"Estado inválido: {self.estado}")
    
    def pausar(self):
        """Pausa una sesión activa."""
        if self.estado != EstadoSesion.ACTIVA:
            raise ValueError("Solo se pueden pausar sesiones activas")
        self.estado = EstadoSesion.PAUSADA
    
    def reanudar(self):
        """Reanuda una sesión pausada."""
        if self.estado != EstadoSesion.PAUSADA:
            raise ValueError("Solo se pueden reanudar sesiones pausadas")
        self.estado = EstadoSesion.ACTIVA
    
    def finalizar(self, fecha_hora_fin: datetime):
        """Finaliza una sesión activa."""
        if self.estado not in [EstadoSesion.ACTIVA, EstadoSesion.PAUSADA]:
            raise ValueError("Solo se pueden finalizar sesiones activas o pausadas")
        
        if fecha_hora_fin < self.fecha_hora_inicio:
            raise ValueError("La fecha de fin no puede ser anterior al inicio")
        
        self.fecha_hora_fin = fecha_hora_fin
        self.tiempo_total_minutos = self._calcular_minutos()
        self.costo_total = self._calcular_costo()
        self.estado = EstadoSesion.FINALIZADA
    
    def extender(self, minutos_adicionales: int):
        """Extiende la duración de una sesión activa."""
        if self.estado != EstadoSesion.ACTIVA:
            raise ValueError("Solo se pueden extender sesiones activas")
        
        if minutos_adicionales <= 0:
            raise ValueError("Los minutos adicionales deben ser positivos")
        
        self.tiempo_total_minutos += minutos_adicionales
        self.costo_total = self._calcular_costo()
    
    def cancelar(self):
        """Cancela una sesión activa."""
        if self.estado != EstadoSesion.ACTIVA:
            raise ValueError("Solo se pueden cancelar sesiones activas")
        self.estado = EstadoSesion.CANCELADA
    
    def _calcular_minutos(self) -> int:
        """Calcula minutos transcurridos."""
        if not self.fecha_hora_fin:
            delta = timezone.now() - self.fecha_hora_inicio
        else:
            delta = self.fecha_hora_fin - self.fecha_hora_inicio
        return int(delta.total_seconds() / 60)
    
    def _calcular_costo(self) -> Decimal:
        """Calcula costo total basado en minutos."""
        horas = Decimal(self.tiempo_total_minutos) / Decimal(60)
        return (horas * self.precio_por_hora).quantize(Decimal('0.01'))
    
    def calcular_costo_actual(self) -> Decimal:
        """Calcula costo actual de la sesión en tiempo real."""
        if self.estado == EstadoSesion.FINALIZADA:
            return self.costo_total
        
        minutos = self._calcular_minutos()
        horas = Decimal(minutos) / Decimal(60)
        return (horas * self.precio_por_hora).quantize(Decimal('0.01'))
