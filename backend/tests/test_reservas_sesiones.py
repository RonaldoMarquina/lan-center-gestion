"""Tests unitarios para Reservas y Sesiones."""
import sys
import os
import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional

# Agregar backend al path para imports
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from core.domain.models.reserva import Reserva, EstadoReserva
from core.domain.models.sesion import Sesion, EstadoSesion
from core.domain.models.cabina import Cabina, TipoCabina, EstadoCabina
from core.application.use_cases.gestionar_reservas import GestionarReservas
from core.application.use_cases.gestionar_sesiones import GestionarSesiones
from core.application.ports.repositories import (
    ReservaRepositoryPort,
    SesionRepositoryPort,
    CabinaRepositoryPort
)


# Repositorios in-memory para testing
class InMemoryReservaRepository(ReservaRepositoryPort):
    def __init__(self):
        self.reservas: List[Reserva] = []
        self.next_id = 1
    
    def guardar(self, reserva: Reserva) -> Reserva:
        if reserva.id is None:
            reserva.id = self.next_id
            self.next_id += 1
            self.reservas.append(reserva)
        else:
            for i, r in enumerate(self.reservas):
                if r.id == reserva.id:
                    self.reservas[i] = reserva
                    break
        return reserva
    
    def obtener_por_id(self, reserva_id: int) -> Optional[Reserva]:
        for r in self.reservas:
            if r.id == reserva_id:
                return r
        return None
    
    def listar_por_usuario(self, usuario_id: int) -> List[Reserva]:
        return [r for r in self.reservas if r.usuario_id == usuario_id]
    
    def listar_por_cabina(self, cabina_id: int) -> List[Reserva]:
        return [r for r in self.reservas if r.cabina_id == cabina_id]
    
    def listar_por_estado(self, estado: EstadoReserva) -> List[Reserva]:
        return [r for r in self.reservas if r.estado == estado]
    
    def buscar_conflictos(self, cabina_id: int, inicio: datetime, fin: datetime) -> List[Reserva]:
        conflictos = []
        for r in self.reservas:
            if r.cabina_id == cabina_id:
                if r.estado in [EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA, EstadoReserva.EN_CURSO]:
                    if r.fecha_hora_inicio < fin and r.fecha_hora_fin > inicio:
                        conflictos.append(r)
        return conflictos
    
    def eliminar(self, reserva_id: int) -> None:
        self.reservas = [r for r in self.reservas if r.id != reserva_id]


class InMemorySesionRepository(SesionRepositoryPort):
    def __init__(self):
        self.sesiones: List[Sesion] = []
        self.next_id = 1
    
    def guardar(self, sesion: Sesion) -> Sesion:
        if sesion.id is None:
            sesion.id = self.next_id
            self.next_id += 1
            self.sesiones.append(sesion)
        else:
            for i, s in enumerate(self.sesiones):
                if s.id == sesion.id:
                    self.sesiones[i] = sesion
                    break
        return sesion
    
    def obtener_por_id(self, sesion_id: int) -> Optional[Sesion]:
        for s in self.sesiones:
            if s.id == sesion_id:
                return s
        return None
    
    def obtener_por_reserva(self, reserva_id: int) -> Optional[Sesion]:
        for s in self.sesiones:
            if s.reserva_id == reserva_id:
                return s
        return None
    
    def listar_por_usuario(self, usuario_id: int) -> List[Sesion]:
        return [s for s in self.sesiones if s.usuario_id == usuario_id]
    
    def listar_por_cabina(self, cabina_id: int) -> List[Sesion]:
        return [s for s in self.sesiones if s.cabina_id == cabina_id]
    
    def listar_activas(self) -> List[Sesion]:
        return [s for s in self.sesiones if s.estado == EstadoSesion.ACTIVA]
    
    def eliminar(self, sesion_id: int) -> None:
        self.sesiones = [s for s in self.sesiones if s.id != sesion_id]


class InMemoryCabinaRepository(CabinaRepositoryPort):
    def __init__(self):
        self.cabinas: List[Cabina] = []
        self.next_id = 1
    
    def guardar(self, cabina: Cabina) -> Cabina:
        if cabina.id is None:
            cabina.id = self.next_id
            self.next_id += 1
            self.cabinas.append(cabina)
        else:
            for i, c in enumerate(self.cabinas):
                if c.id == cabina.id:
                    self.cabinas[i] = cabina
                    break
        return cabina
    
    def obtener_por_id(self, cabina_id: int) -> Optional[Cabina]:
        for c in self.cabinas:
            if c.id == cabina_id:
                return c
        return None
    
    def buscar_por_numero(self, numero: int) -> Optional[Cabina]:
        for c in self.cabinas:
            if c.numero == numero:
                return c
        return None
    
    def buscar_por_estado(self, estado: EstadoCabina) -> List[Cabina]:
        return [c for c in self.cabinas if c.estado == estado]
    
    def listar_todas(self) -> List[Cabina]:
        return self.cabinas.copy()
    
    def eliminar(self, cabina_id: int) -> None:
        self.cabinas = [c for c in self.cabinas if c.id != cabina_id]


# Tests de dominio
class TestReservaDominio(unittest.TestCase):
    def test_crear_reserva_valida(self):
        inicio = datetime.now()
        fin = inicio + timedelta(hours=2)
        reserva = Reserva(
            id=None,
            usuario_id=1,
            cabina_id=1,
            fecha_hora_inicio=inicio,
            fecha_hora_fin=fin,
            estado=EstadoReserva.PENDIENTE,
            creada_en=datetime.now()
        )
        self.assertEqual(reserva.estado, EstadoReserva.PENDIENTE)
        self.assertEqual(reserva.duracion_minutos(), 120)
    
    def test_reserva_fin_antes_inicio_error(self):
        inicio = datetime.now()
        fin = inicio - timedelta(hours=1)
        with self.assertRaises(ValueError):
            Reserva(
                id=None,
                usuario_id=1,
                cabina_id=1,
                fecha_hora_inicio=inicio,
                fecha_hora_fin=fin,
                estado=EstadoReserva.PENDIENTE,
                creada_en=datetime.now()
            )
    
    def test_transiciones_estado_reserva(self):
        inicio = datetime.now()
        fin = inicio + timedelta(hours=1)
        reserva = Reserva(
            id=1,
            usuario_id=1,
            cabina_id=1,
            fecha_hora_inicio=inicio,
            fecha_hora_fin=fin,
            estado=EstadoReserva.PENDIENTE,
            creada_en=datetime.now()
        )
        reserva.confirmar()
        self.assertEqual(reserva.estado, EstadoReserva.CONFIRMADA)
        reserva.iniciar()
        self.assertEqual(reserva.estado, EstadoReserva.EN_CURSO)
        reserva.completar()
        self.assertEqual(reserva.estado, EstadoReserva.COMPLETADA)
    
    def test_conflicto_horario(self):
        inicio1 = datetime(2025, 11, 19, 10, 0)
        fin1 = datetime(2025, 11, 19, 12, 0)
        reserva1 = Reserva(
            id=1, usuario_id=1, cabina_id=1,
            fecha_hora_inicio=inicio1, fecha_hora_fin=fin1,
            estado=EstadoReserva.CONFIRMADA, creada_en=datetime.now()
        )
        
        inicio2 = datetime(2025, 11, 19, 11, 0)
        fin2 = datetime(2025, 11, 19, 13, 0)
        reserva2 = Reserva(
            id=2, usuario_id=2, cabina_id=1,
            fecha_hora_inicio=inicio2, fecha_hora_fin=fin2,
            estado=EstadoReserva.PENDIENTE, creada_en=datetime.now()
        )
        
        self.assertTrue(reserva1.tiene_conflicto(reserva2))


class TestSesionDominio(unittest.TestCase):
    def test_crear_sesion_valida(self):
        inicio = datetime.now()
        sesion = Sesion(
            id=None,
            reserva_id=1,
            cabina_id=1,
            usuario_id=1,
            fecha_hora_inicio=inicio,
            fecha_hora_fin=None,
            tiempo_total_minutos=0,
            costo_total=Decimal('0.00'),
            precio_por_hora=Decimal('5.00'),
            estado=EstadoSesion.ACTIVA
        )
        self.assertEqual(sesion.estado, EstadoSesion.ACTIVA)
    
    def test_finalizar_sesion_calcula_costo(self):
        inicio = datetime.now()
        sesion = Sesion(
            id=1,
            reserva_id=1,
            cabina_id=1,
            usuario_id=1,
            fecha_hora_inicio=inicio,
            fecha_hora_fin=None,
            tiempo_total_minutos=0,
            costo_total=Decimal('0.00'),
            precio_por_hora=Decimal('6.00'),
            estado=EstadoSesion.ACTIVA
        )
        fin = inicio + timedelta(hours=2)
        sesion.finalizar(fin)
        self.assertEqual(sesion.estado, EstadoSesion.FINALIZADA)
        self.assertEqual(sesion.tiempo_total_minutos, 120)
        self.assertEqual(sesion.costo_total, Decimal('12.00'))
    
    def test_extender_sesion(self):
        inicio = datetime.now()
        sesion = Sesion(
            id=1, reserva_id=1, cabina_id=1, usuario_id=1,
            fecha_hora_inicio=inicio, fecha_hora_fin=None,
            tiempo_total_minutos=60, costo_total=Decimal('5.00'),
            precio_por_hora=Decimal('5.00'), estado=EstadoSesion.ACTIVA
        )
        sesion.extender(30)
        self.assertEqual(sesion.tiempo_total_minutos, 90)


# Tests de casos de uso
class TestGestionarReservasUseCase(unittest.TestCase):
    def setUp(self):
        self.reserva_repo = InMemoryReservaRepository()
        self.cabina_repo = InMemoryCabinaRepository()
        self.use_case = GestionarReservas(self.reserva_repo, self.cabina_repo)
        
        # Crear cabina de prueba
        cabina = Cabina(
            id=None, numero=1, tipo=TipoCabina.BASICA,
            estado=EstadoCabina.DISPONIBLE, especificaciones={},
            precio_por_hora=5.0
        )
        self.cabina = self.cabina_repo.guardar(cabina)
    
    def test_crear_reserva_exitosa(self):
        inicio = datetime.now() + timedelta(hours=1)
        fin = inicio + timedelta(hours=2)
        reserva = self.use_case.crear_reserva(1, self.cabina.id, inicio, fin)
        self.assertIsNotNone(reserva.id)
        self.assertEqual(reserva.estado, EstadoReserva.PENDIENTE)
    
    def test_crear_reserva_con_conflicto_error(self):
        inicio1 = datetime.now() + timedelta(hours=1)
        fin1 = inicio1 + timedelta(hours=2)
        self.use_case.crear_reserva(1, self.cabina.id, inicio1, fin1)
        
        inicio2 = inicio1 + timedelta(minutes=30)
        fin2 = fin1 + timedelta(hours=1)
        with self.assertRaises(ValueError):
            self.use_case.crear_reserva(2, self.cabina.id, inicio2, fin2)


class TestGestionarSesionesUseCase(unittest.TestCase):
    def setUp(self):
        self.sesion_repo = InMemorySesionRepository()
        self.reserva_repo = InMemoryReservaRepository()
        self.cabina_repo = InMemoryCabinaRepository()
        self.use_case = GestionarSesiones(
            self.sesion_repo,
            self.reserva_repo,
            self.cabina_repo
        )
        
        # Crear cabina y reserva
        cabina = Cabina(
            id=None, numero=1, tipo=TipoCabina.BASICA,
            estado=EstadoCabina.DISPONIBLE, especificaciones={},
            precio_por_hora=5.0
        )
        self.cabina = self.cabina_repo.guardar(cabina)
        
        inicio = datetime.now()
        fin = inicio + timedelta(hours=2)
        reserva = Reserva(
            id=None, usuario_id=1, cabina_id=self.cabina.id,
            fecha_hora_inicio=inicio, fecha_hora_fin=fin,
            estado=EstadoReserva.CONFIRMADA, creada_en=datetime.now()
        )
        self.reserva = self.reserva_repo.guardar(reserva)
    
    def test_iniciar_sesion_exitosa(self):
        sesion = self.use_case.iniciar_sesion(self.reserva.id)
        self.assertIsNotNone(sesion.id)
        self.assertEqual(sesion.estado, EstadoSesion.ACTIVA)
        
        # Verificar que cabina está ocupada
        cabina_actualizada = self.cabina_repo.obtener_por_id(self.cabina.id)
        self.assertEqual(cabina_actualizada.estado, EstadoCabina.OCUPADA)
    
    def test_finalizar_sesion_libera_cabina(self):
        sesion = self.use_case.iniciar_sesion(self.reserva.id)
        sesion_finalizada = self.use_case.finalizar_sesion(sesion.id)
        
        self.assertEqual(sesion_finalizada.estado, EstadoSesion.FINALIZADA)
        self.assertGreaterEqual(sesion_finalizada.costo_total, Decimal('0'))
        
        # Verificar que cabina está libre
        cabina_actualizada = self.cabina_repo.obtener_por_id(self.cabina.id)
        self.assertEqual(cabina_actualizada.estado, EstadoCabina.DISPONIBLE)


if __name__ == '__main__':
    unittest.main()
