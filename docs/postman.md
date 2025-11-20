# Guía de Pruebas con Postman

Esta guía documenta todos los endpoints de la API del LAN Center con método, URL, body requerido y autenticación.

## Configuración Inicial

**Base URL:** `http://127.0.0.1:8000`

**Token de Autenticación:**  
Todos los endpoints (excepto Auth) requieren header:
```
Authorization: Bearer {{access_token}}
```

---

## AUTH

### Obtener Token
**POST** `/api/auth/token/`  
**Body:**
```json
{
  "username": "testuser",
  "password": "testpass123"
}
```
**Token:** NO

### Refrescar Token
**POST** `/api/auth/token/refresh/`  
**Body:**
```json
{
  "refresh": "<tu_refresh_token>"
}
```
**Token:** NO

---

## CABINAS

### Listar Cabinas
**GET** `/api/cabinas/`  
**Body:** —  
**Token:** SÍ

### Crear Cabina
**POST** `/api/cabinas/`  
**Body:**
```json
{
  "numero": 1,
  "tipo": "BASICA",
  "precio_por_hora": "5.00",
  "especificaciones": {
    "cpu": "Intel i5",
    "ram": "8GB"
  }
}
```
**Token:** SÍ

### Obtener Cabina
**GET** `/api/cabinas/{id}/`  
**Body:** —  
**Token:** SÍ

### Actualizar Cabina
**PUT/PATCH** `/api/cabinas/{id}/`  
**Body:**
```json
{
  "tipo": "GAMER",
  "precio_por_hora": "8.00"
}
```
**Token:** SÍ

### Eliminar Cabina
**DELETE** `/api/cabinas/{id}/`  
**Body:** —  
**Token:** SÍ

### Ocupar Cabina
**POST** `/api/cabinas/{id}/ocupar/`  
**Body:** —  
**Token:** SÍ

### Liberar Cabina
**POST** `/api/cabinas/{id}/liberar/`  
**Body:** —  
**Token:** SÍ

### Poner en Mantenimiento
**POST** `/api/cabinas/{id}/mantenimiento/`  
**Body:** —  
**Token:** SÍ

---

## RESERVAS

### Listar Reservas
**GET** `/api/reservas/`  
**Body:** —  
**Token:** SÍ  
**Filtros query:** `?usuario_id=1&cabina_id=1&activas=true`

### Crear Reserva
**POST** `/api/reservas/`  
**Body:**
```json
{
  "usuario_id": 1,
  "cabina_id": 1,
  "fecha_hora_inicio": "2025-11-19T10:00:00Z",
  "fecha_hora_fin": "2025-11-19T11:00:00Z"
}
```
**Token:** SÍ

### Obtener Reserva
**GET** `/api/reservas/{id}/`  
**Body:** —  
**Token:** SÍ

### Confirmar Reserva
**POST** `/api/reservas/{id}/confirmar/`  
**Body:** —  
**Token:** SÍ

### Iniciar Reserva
**POST** `/api/reservas/{id}/iniciar/`  
**Body:** —  
**Token:** SÍ

### Cancelar Reserva
**POST** `/api/reservas/{id}/cancelar/`  
**Body:** —  
**Token:** SÍ

---

## SESIONES

### Listar Sesiones
**GET** `/api/sesiones/`  
**Body:** —  
**Token:** SÍ  
**Filtros query:** `?usuario_id=1&activas=true`

### Iniciar Sesión
**POST** `/api/sesiones/`  
**Body:**
```json
{
  "reserva_id": 1
}
```
**Token:** SÍ

### Obtener Sesión
**GET** `/api/sesiones/{id}/`  
**Body:** —  
**Token:** SÍ

### Finalizar Sesión
**POST** `/api/sesiones/{id}/finalizar/`  
**Body:** —  
**Token:** SÍ

### Extender Sesión
**POST** `/api/sesiones/{id}/extender/`  
**Body:**
```json
{
  "minutos_adicionales": 30
}
```
**Token:** SÍ

### Pausar Sesión
**POST** `/api/sesiones/{id}/pausar/`  
**Body:** —  
**Token:** SÍ

### Reanudar Sesión
**POST** `/api/sesiones/{id}/reanudar/`  
**Body:** —  
**Token:** SÍ

### Cancelar Sesión
**POST** `/api/sesiones/{id}/cancelar/`  
**Body:** —  
**Token:** SÍ

### Costo Actual
**GET** `/api/sesiones/{id}/costo-actual/`  
**Body:** —  
**Token:** SÍ

---

## PAGOS

### Listar Pagos (Historial)
**GET** `/api/pagos/`  
**Body:** —  
**Token:** SÍ  
**Filtros query:** `?usuario_id=1&estado=completado&fecha_desde=2025-11-01&fecha_hasta=2025-11-30`

### Registrar Pago
**POST** `/api/pagos/`  
**Body:**
```json
{
  "sesion_id": 1,
  "monto": "5.00",
  "metodo_pago": "efectivo",
  "notas": "Pago en efectivo"
}
```
**Token:** SÍ  
**Nota:** Sesión debe estar FINALIZADA

### Obtener Pago
**GET** `/api/pagos/{id}/`  
**Body:** —  
**Token:** SÍ

### Completar Pago
**POST** `/api/pagos/{id}/completar/`  
**Body (opcional):**
```json
{
  "comprobante_numero": "REC-001"
}
```
**Token:** SÍ  
**Nota:** Si no envías comprobante se genera automático

### Marcar Pago Fallido
**POST** `/api/pagos/{id}/marcar-fallido/`  
**Body:**
```json
{
  "motivo": "Tarjeta rechazada"
}
```
**Token:** SÍ

### Reembolsar Pago
**POST** `/api/pagos/{id}/reembolsar/`  
**Body:**
```json
{
  "motivo": "Error en cobro"
}
```
**Token:** SÍ  
**Nota:** Solo pagos COMPLETADOS pueden reembolsarse

### Obtener Comprobante
**GET** `/api/pagos/{id}/comprobante/`  
**Body:** —  
**Token:** SÍ

---

## FLUJO COMPLETO RECOMENDADO

1. **Autenticación:** POST `/api/auth/token/` → guardar `access_token`
2. **Crear Cabina:** POST `/api/cabinas/` → guardar `cabina_id`
3. **Crear Reserva:** POST `/api/reservas/` → guardar `reserva_id`
4. **Confirmar Reserva:** POST `/api/reservas/{reserva_id}/confirmar/`
5. **Iniciar Sesión:** POST `/api/sesiones/` con `reserva_id` → guardar `sesion_id`
6. **Finalizar Sesión:** POST `/api/sesiones/{sesion_id}/finalizar/`
7. **Registrar Pago:** POST `/api/pagos/` con `sesion_id` → guardar `pago_id`
8. **Completar Pago:** POST `/api/pagos/{pago_id}/completar/`
9. **Ver Comprobante:** GET `/api/pagos/{pago_id}/comprobante/`
10. **Historial Usuario:** GET `/api/pagos/?usuario_id=1`

---

## VARIABLES POSTMAN SUGERIDAS

| Variable | Valor Inicial |
|----------|---------------|
| base_url | http://127.0.0.1:8000 |
| access_token | (copiar de respuesta auth) |
| cabina_id | (copiar de respuesta crear cabina) |
| reserva_id | (copiar de respuesta crear reserva) |
| sesion_id | (copiar de respuesta iniciar sesión) |
| pago_id | (copiar de respuesta registrar pago) |

---

## VALORES VÁLIDOS

**Tipo Cabina:** `BASICA`, `GAMER`, `VIP`  
**Método Pago:** `efectivo`, `tarjeta`, `transferencia`, `billetera_digital`  
**Formato Fecha:** ISO8601 UTC `2025-11-19T10:00:00Z`

---

Última actualización: 2025-11-19
