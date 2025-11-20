## Flujo Cabinas (Clean + Hexagonal)

Dominio: `Cabina` define reglas de estado.
Aplicación: `GestionarCabinas` orquesta validaciones y usa puerto `CabinaRepositoryPort`.
Infraestructura: `CabinaModel` (Django) + `DjangoCabinaRepository` adaptan persistencia.
Presentación: `CabinaViewSet` y serializers exponen endpoints REST.

Secuencia crear cabina:
1. POST /cabinas/ -> ViewSet valida input.
2. Use case verifica número único (repo.buscar_por_numero).
3. Crea entidad dominio y repo.guardar (ORM).
4. Devuelve representación serializada.

Cambio de estado (ej. ocupar):
1. POST /cabinas/{id}/ocupar.
2. Use case obtiene cabina (repo.obtener_por_id) y llama `cabina.ocupar()`.
3. Persiste cambios y retorna cabina.

Eliminar:
1. DELETE /cabinas/{id}/.
2. Adapter valida estado != OCUPADA antes de borrar.

Beneficios:
- Dominio independiente del framework.
- Adaptadores intercambiables (otro ORM / API externa) si implementan puerto.
- Test rápido con repositorio en memoria.

---

## Flujo Reservas y Sesiones (Clean + Hexagonal)

### Entidades de Dominio

**Reserva:**
- Estados: PENDIENTE → CONFIRMADA → EN_CURSO → COMPLETADA (o CANCELADA)
- Validaciones: fecha_fin > fecha_inicio, detección de conflictos de horario
- Métodos: confirmar(), iniciar(), completar(), cancelar()

**Sesion:**
- Estados: ACTIVA → FINALIZADA (o PAUSADA/CANCELADA)
- Cálculo de costo: precio_por_hora * (minutos / 60)
- Métodos: finalizar(), extender(), pausar(), reanudar(), calcular_costo_actual()

### Arquitectura en Capas

**Dominio:**
- `Reserva` y `Sesion` con lógica de negocio pura
- Enums: `EstadoReserva`, `EstadoSesion`
- Validaciones de transiciones de estado

**Aplicación:**
- `GestionarReservas`: crear_reserva (valida conflictos), confirmar, iniciar, cancelar
- `GestionarSesiones`: iniciar_sesion (desde reserva), finalizar, extender, calcular_costo_actual
- Puertos: `ReservaRepositoryPort`, `SesionRepositoryPort`

**Infraestructura:**
- `ReservaModel` y `SesionModel` con ForeignKey a User y CabinaModel
- `DjangoReservaRepository`: búsqueda de conflictos con Q objects
- `DjangoSesionRepository`: gestión de sesiones activas
- Migrations aplicadas a SQL Server

**Presentación:**
- `ReservaViewSet`: CRUD + acciones (confirmar, iniciar, cancelar)
- `SesionViewSet`: CRUD + acciones (finalizar, extender, pausar, reanudar, costo-actual)
- Serializers con conversión de enums a valores string

### Flujo Completo: Reserva → Sesión → Pago

1. **Crear Reserva:**
   - POST /reservas/ con usuario_id, cabina_id, fechas
   - Use case valida: cabina existe y disponible
   - Busca conflictos de horario (buscar_conflictos)
   - Crea reserva en estado PENDIENTE

2. **Confirmar Reserva:**
   - POST /reservas/{id}/confirmar/
   - Transición PENDIENTE → CONFIRMADA
   - Valida estado actual antes de confirmar

3. **Iniciar Sesión:**
   - POST /sesiones/ con reserva_id
   - Valida reserva CONFIRMADA
   - Crea sesión ACTIVA con timestamp inicial
   - Marca reserva como EN_CURSO
   - Cambia cabina a OCUPADA

4. **Calcular Costo en Tiempo Real:**
   - GET /sesiones/{id}/costo-actual/
   - Calcula minutos transcurridos desde inicio
   - Retorna costo actual sin finalizar sesión

5. **Extender Sesión (opcional):**
   - POST /sesiones/{id}/extender/ con minutos_adicionales
   - Incrementa tiempo_total_minutos
   - Recalcula costo_total

6. **Finalizar Sesión:**
   - POST /sesiones/{id}/finalizar/
   - Registra fecha_hora_fin
   - Calcula tiempo_total_minutos y costo_total
   - Transición ACTIVA → FINALIZADA
   - Marca reserva como COMPLETADA
   - Libera cabina (OCUPADA → DISPONIBLE)

### Validaciones de Negocio

- **Conflictos de horario:** No permite reservas solapadas en misma cabina
- **Transiciones de estado:** Solo permite transiciones válidas (ej: no cancelar sesión finalizada)
- **Cabina en mantenimiento:** No permite reservar cabinas desactivadas o en mantenimiento
- **Timezone aware:** Todas las fechas usan Django timezone para consistencia

### Endpoints API

**Reservas:**
- GET /reservas/ - Lista con filtros (usuario_id, cabina_id, activas)
- GET /reservas/{id}/ - Detalle de reserva
- POST /reservas/ - Crear nueva reserva
- POST /reservas/{id}/confirmar/ - Confirmar pendiente
- POST /reservas/{id}/iniciar/ - Iniciar confirmada
- POST /reservas/{id}/cancelar/ - Cancelar reserva

**Sesiones:**
- GET /sesiones/ - Lista con filtros (usuario_id, activas=true)
- GET /sesiones/{id}/ - Detalle de sesión
- POST /sesiones/ - Iniciar desde reserva
- POST /sesiones/{id}/finalizar/ - Finalizar y calcular costo
- POST /sesiones/{id}/extender/ - Extender tiempo
- POST /sesiones/{id}/pausar/ - Pausar activa
- POST /sesiones/{id}/reanudar/ - Reanudar pausada
- POST /sesiones/{id}/cancelar/ - Cancelar sesión
- GET /sesiones/{id}/costo-actual/ - Costo en tiempo real

### Testing

**Tests Unitarios (11 tests):**
- Dominio: transiciones de estado, validaciones, cálculo de costos
- Casos de uso: crear reserva, conflictos, iniciar/finalizar sesión
- Repositorios in-memory para tests aislados

**Tests de Integración API (7 tests):**
- Flujo completo reserva → sesión
- Conflictos de horario (400 Bad Request)
- Cancelar reservas y sesiones
- Extender sesión activa
- Calcular costo actual
- Listar sesiones activas
- Verificar liberación de cabina

### Beneficios de la Arquitectura

- **Lógica de negocio centralizada:** Reglas en entidades de dominio, no dispersas
- **Testeable:** Tests unitarios sin base de datos (repositorios in-memory)
- **Mantenible:** Cambios en persistencia no afectan dominio
- **Escalable:** Puertos permiten cambiar a Redis, MongoDB, etc sin tocar casos de uso
- **Trazabilidad:** Estados explícitos facilitan auditoría y reporting
