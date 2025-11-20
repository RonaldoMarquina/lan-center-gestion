"""Entidad de dominio Pago."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class MetodoPago(Enum):
    """Métodos de pago disponibles."""
    EFECTIVO = "efectivo"
    TARJETA = "tarjeta"
    TRANSFERENCIA = "transferencia"
    BILLETERA_DIGITAL = "billetera_digital"


class EstadoPago(Enum):
    """Estados posibles de un pago."""
    PENDIENTE = "pendiente"
    COMPLETADO = "completado"
    FALLIDO = "fallido"
    REEMBOLSADO = "reembolsado"


@dataclass
class Pago:
    """Representa un pago de servicio."""
    
    id: Optional[int]
    sesion_id: int
    usuario_id: int
    monto: Decimal
    metodo_pago: MetodoPago
    estado: EstadoPago
    fecha_pago: datetime
    comprobante_numero: Optional[str]
    notas: str
    
    def __post_init__(self):
        """Valida invariantes del dominio."""
        if self.monto <= 0:
            raise ValueError("El monto debe ser mayor a cero")
        
        if self.metodo_pago not in MetodoPago:
            raise ValueError(f"Método de pago inválido: {self.metodo_pago}")
        
        if self.estado not in EstadoPago:
            raise ValueError(f"Estado de pago inválido: {self.estado}")
    
    def completar(self, comprobante_numero: str):
        """Marca el pago como completado."""
        if self.estado != EstadoPago.PENDIENTE:
            raise ValueError("Solo se pueden completar pagos pendientes")
        
        if not comprobante_numero:
            raise ValueError("Se requiere número de comprobante")
        
        self.estado = EstadoPago.COMPLETADO
        self.comprobante_numero = comprobante_numero
    
    def marcar_fallido(self, motivo: str):
        """Marca el pago como fallido."""
        if self.estado != EstadoPago.PENDIENTE:
            raise ValueError("Solo se pueden marcar como fallidos pagos pendientes")
        
        self.estado = EstadoPago.FALLIDO
        self.notas = f"{self.notas} | FALLIDO: {motivo}"
    
    def reembolsar(self, motivo: str):
        """Reembolsa un pago completado."""
        if self.estado != EstadoPago.COMPLETADO:
            raise ValueError("Solo se pueden reembolsar pagos completados")
        
        self.estado = EstadoPago.REEMBOLSADO
        self.notas = f"{self.notas} | REEMBOLSO: {motivo}"
    
    def generar_numero_comprobante(self, prefijo: str = "COMP") -> str:
        """Genera un número de comprobante."""
        timestamp = self.fecha_pago.strftime("%Y%m%d%H%M%S")
        return f"{prefijo}-{timestamp}-{self.id or 0}"
