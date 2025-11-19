
"""Pruebas unitarias básicas para el dominio Cabina y caso de uso GestionarCabinas.

Incluye:
 - Validaciones y transiciones de estado de la entidad Cabina
 - Creación de cabina vía caso de uso y manejo de duplicados

Se emplea unittest para evitar dependencias adicionales.
"""

import unittest

from backend.core.domain.models.cabina import (
	Cabina,
	TipoCabina,
	EstadoCabina,
)
from backend.core.application.use_cases.gestionar_cabinas import GestionarCabinas
from backend.core.application.ports.repositories import CabinaRepositoryPort


class InMemoryCabinaRepository(CabinaRepositoryPort):
	"""Implementación en memoria para pruebas del puerto de repositorio."""

	def __init__(self) -> None:
		self._data = {}
		self._next_id = 1

	def guardar(self, cabina: Cabina) -> Cabina:
		if cabina.id is None:
			cabina.id = self._next_id
			self._next_id += 1
		self._data[cabina.id] = cabina
		return cabina

	def obtener_por_id(self, cabina_id: int):  # type: ignore[override]
		return self._data.get(cabina_id)

	def buscar_por_numero(self, numero: int):  # type: ignore[override]
		for c in self._data.values():
			if c.numero == numero:
				return c
		return None

	def buscar_por_estado(self, estado: EstadoCabina):  # type: ignore[override]
		return [c for c in self._data.values() if c.estado == estado]

	def listar_todas(self):  # type: ignore[override]
		return list(self._data.values())

	def eliminar(self, cabina_id: int) -> None:  # type: ignore[override]
		cab = self._data.get(cabina_id)
		if not cab:
			return
		if cab.estado == EstadoCabina.OCUPADA:
			raise ValueError("No se puede eliminar una cabina ocupada")
		del self._data[cabina_id]


class TestCabinaDominio(unittest.TestCase):
	def setUp(self) -> None:
		self.cabina = Cabina(
			id=None,
			numero=1,
			tipo=TipoCabina.GAMER,
			estado=EstadoCabina.DISPONIBLE,
			especificaciones={"cpu": "Ryzen", "gpu": "RTX"},
			precio_por_hora=10.0,
		)

	def test_ocupar_transicion_valida(self):
		self.cabina.ocupar()
		self.assertEqual(self.cabina.estado, EstadoCabina.OCUPADA)

	def test_ocupar_invalida_si_no_disponible(self):
		self.cabina.estado = EstadoCabina.MANTENIMIENTO
		with self.assertRaises(ValueError):
			self.cabina.ocupar()

	def test_mantenimiento_flow(self):
		self.cabina.iniciar_mantenimiento()
		self.assertEqual(self.cabina.estado, EstadoCabina.MANTENIMIENTO)
		self.cabina.finalizar_mantenimiento()
		self.assertEqual(self.cabina.estado, EstadoCabina.DISPONIBLE)

	def test_desactivar_y_activar(self):
		self.cabina.desactivar()
		self.assertEqual(self.cabina.estado, EstadoCabina.DESACTIVADA)
		self.cabina.activar()
		self.assertEqual(self.cabina.estado, EstadoCabina.DISPONIBLE)

	def test_actualizar_precio(self):
		self.cabina.actualizar_precio(15.5)
		self.assertEqual(self.cabina.precio_por_hora, 15.5)
		with self.assertRaises(ValueError):
			self.cabina.actualizar_precio(0)


class TestGestionarCabinasUseCase(unittest.TestCase):
	def setUp(self) -> None:
		self.repo = InMemoryCabinaRepository()
		self.uc = GestionarCabinas(self.repo)

	def test_crear_cabina_exito(self):
		cabina = self.uc.crear_cabina(
			numero=5,
			tipo="gamer",
			especificaciones={"cpu": "Intel", "gpu": "RTX"},
			precio_por_hora=12.0,
		)
		self.assertIsNotNone(cabina.id)
		self.assertEqual(cabina.numero, 5)
		self.assertEqual(cabina.estado, EstadoCabina.DISPONIBLE)

	def test_crear_cabina_numero_duplicado(self):
		self.uc.crear_cabina(
			numero=5,
			tipo="vip",
			especificaciones={},
			precio_por_hora=20.0,
		)
		with self.assertRaises(ValueError):
			self.uc.crear_cabina(
				numero=5,
				tipo="basica",
				especificaciones={},
				precio_por_hora=8.0,
			)

	def test_ocupar_y_liberar_via_use_case(self):
		cabina = self.uc.crear_cabina(
			numero=9,
			tipo="basica",
			especificaciones={},
			precio_por_hora=5.0,
		)
		actualizado = self.uc.ocupar_cabina(cabina.id)
		self.assertEqual(actualizado.estado, EstadoCabina.OCUPADA)
		actualizado = self.uc.liberar_cabina(cabina.id)
		self.assertEqual(actualizado.estado, EstadoCabina.DISPONIBLE)


if __name__ == "__main__":  # pragma: no cover
	unittest.main(verbosity=2)

