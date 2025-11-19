"""Tests de API para cabinas (básicos).

Usa SQLite en memoria para aislar de SQL Server real.
"""

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework import status


@override_settings(
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
)
class CabinaApiTests(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="tester", password="pass12345")
        # Obtener token
        resp = self.client.post(
            "/api/auth/token/",
            {"username": "tester", "password": "pass12345"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.token = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_crear_y_listar(self):
        r = self.client.post(
            "/api/cabinas/",
            {
                "numero": 77,
                "tipo": "gamer",
                "especificaciones": {"cpu": "Ryzen"},
                "precio_por_hora": 9.5,
            },
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        r2 = self.client.get("/api/cabinas/")
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        self.assertTrue(any(c["numero"] == 77 for c in r2.data))

    def test_ocupar_libera_flujo(self):
        r = self.client.post(
            "/api/cabinas/",
            {
                "numero": 88,
                "tipo": "basica",
                "especificaciones": {},
                "precio_por_hora": 5.0,
            },
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        cab_id = r.data["id"]
        r3 = self.client.post(f"/api/cabinas/{cab_id}/ocupar/")
        self.assertEqual(r3.status_code, status.HTTP_200_OK)
        r4 = self.client.post(f"/api/cabinas/{cab_id}/liberar/")
        self.assertEqual(r4.status_code, status.HTTP_200_OK)

    def test_crear_duplicado_numero(self):
        r1 = self.client.post(
            "/api/cabinas/",
            {"numero": 10, "tipo": "vip", "especificaciones": {}, "precio_por_hora": 20.0},
            format="json",
        )
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)
        r2 = self.client.post(
            "/api/cabinas/",
            {"numero": 10, "tipo": "gamer", "especificaciones": {}, "precio_por_hora": 15.0},
            format="json",
        )
        self.assertEqual(r2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", r2.data)

    def test_disponibles_endpoint(self):
        r1 = self.client.post(
            "/api/cabinas/",
            {"numero": 21, "tipo": "basica", "especificaciones": {}, "precio_por_hora": 6.0},
            format="json",
        )
        r2 = self.client.post(
            "/api/cabinas/",
            {"numero": 22, "tipo": "gamer", "especificaciones": {}, "precio_por_hora": 8.0},
            format="json",
        )
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r2.status_code, status.HTTP_201_CREATED)
        cab2 = r2.data["id"]
        self.client.post(f"/api/cabinas/{cab2}/ocupar/")
        resp = self.client.get("/api/cabinas/disponibles/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        numeros = [c["numero"] for c in resp.data]
        self.assertIn(21, numeros)
        self.assertNotIn(22, numeros)

    def test_mantenimiento_y_ocupar_invalido(self):
        r = self.client.post(
            "/api/cabinas/",
            {"numero": 31, "tipo": "gamer", "especificaciones": {}, "precio_por_hora": 11.0},
            format="json",
        )
        cab_id = r.data["id"]
        r_m = self.client.post(f"/api/cabinas/{cab_id}/mantenimiento/iniciar/")
        self.assertEqual(r_m.status_code, status.HTTP_200_OK)
        r_bad = self.client.post(f"/api/cabinas/{cab_id}/ocupar/")
        self.assertEqual(r_bad.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_ocupada_rechazado(self):
        r = self.client.post(
            "/api/cabinas/",
            {"numero": 41, "tipo": "basica", "especificaciones": {}, "precio_por_hora": 5.0},
            format="json",
        )
        cab_id = r.data["id"]
        self.client.post(f"/api/cabinas/{cab_id}/ocupar/")
        d = self.client.delete(f"/api/cabinas/{cab_id}/")
        self.assertEqual(d.status_code, status.HTTP_400_BAD_REQUEST)

    def test_actualizar_precio(self):
        r = self.client.post(
            "/api/cabinas/",
            {"numero": 51, "tipo": "vip", "especificaciones": {}, "precio_por_hora": 25.0},
            format="json",
        )
        cab_id = r.data["id"]
        bad = self.client.patch(f"/api/cabinas/{cab_id}/precio/", {"precio_por_hora": 0}, format="json")
        self.assertEqual(bad.status_code, status.HTTP_400_BAD_REQUEST)
        ok = self.client.patch(
            f"/api/cabinas/{cab_id}/precio/", {"precio_por_hora": 30.5}, format="json"
        )
        self.assertEqual(ok.status_code, status.HTTP_200_OK)
        self.assertEqual(ok.data["precio_por_hora"], 30.5)
