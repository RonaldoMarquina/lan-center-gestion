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

7. **Registrar Pago (Sesión Finalizada):**
   - POST /pagos/ con sesion_id, monto, metodo_pago
   - Valida: sesión FINALIZADA y sin pago previo (OneToOne)
   - Crea pago en estado PENDIENTE

8. **Completar Pago:**
   - POST /pagos/{id}/completar/ (opcional comprobante_numero)
   - Si no se envía comprobante, genera uno automático prefijado "COMP-" + timestamp
   - Transición PENDIENTE → COMPLETADO

9. **Comprobante:**
   - GET /pagos/{id}/comprobante/ devuelve número, monto, método y sesión asociada

10. **Marcar Pago Fallido:**
    - POST /pagos/{id}/marcar-fallido/ con motivo
    - Transición PENDIENTE → FALLIDO (no puede luego completarse)

11. **Reembolsar Pago:**
    - POST /pagos/{id}/reembolsar/ con motivo
    - Solo si estado actual = COMPLETADO → REEMBOLSADO

12. **Historial Usuario:**
    - GET /pagos/?usuario_id=XXX lista pagos (filtros por estado, fecha desde/hasta)

### Módulo Pagos (RF17–RF19)

**Entidad Dominio `Pago`:**
- Atributos: id, sesion_id, usuario_id, monto (Decimal>0), metodo_pago, estado_pago, fecha_pago, comprobante_numero, notas
- Estados (`EstadoPago`): PENDIENTE, COMPLETADO, FALLIDO, REEMBOLSADO
- Métodos: completar(), marcar_fallido(), reembolsar(), generar_numero_comprobante(prefijo="COMP")
- Reglas:
  - Sólo pagos PENDIENTE pueden completarse o marcarse fallidos
  - Sólo pagos COMPLETADO pueden reembolsarse
  - Generar comprobante si falta al completar

**Método de Pago (`MetodoPago`):** EFECTIVO, TARJETA, TRANSFERENCIA, BILLETERA_DIGITAL

**Puerto `PagoRepositoryPort`:**
- guardar, obtener_por_id, obtener_por_sesion, listar_por_usuario, listar_por_estado, listar_por_fecha(desde,hasta), eliminar

**Caso de Uso `ProcesarPagos`:**
- registrar_pago(sesion_id, monto, metodo) valida sesión FINALIZADA
- completar_pago(pago_id, comprobante?) genera comprobante si no se pasa
- marcar_pago_fallido(pago_id, motivo)
- reembolsar_pago(pago_id, motivo)
- obtener_historial_usuario(usuario_id)
- generar_comprobante(pago_id) (para fallback)

**Persistencia `PagoModel`:**
- OneToOneField a `SesionModel` (garantiza un pago por sesión)
- Campos: monto, metodo_pago (lowercase), estado (lowercase), fecha_pago, comprobante_numero (único), notas
- Índices: (usuario, estado), fecha_pago, comprobante_numero

**Adaptador `DjangoPagoRepository`:**
- Filtros por estado (lowercase) y rangos de fecha
- Conversión enum almacenado en minúscula ↔ dominio en mayúscula

**API Endpoints Pagos:**
- POST /pagos/ (crear pago pendiente)
- POST /pagos/{id}/completar/
- POST /pagos/{id}/marcar-fallido/
- POST /pagos/{id}/reembolsar/
- GET  /pagos/{id}/comprobante/
- GET  /pagos/ (filtros: usuario_id, estado, fecha_desde, fecha_hasta)

**Validaciones Clave:**
- Sesión debe estar FINALIZADA para registrar pago
- Un pago por sesión (OneToOne)
- Monto > 0
- Transiciones controladas y exclusivas

**Testing:**
- Unit tests (13): estados, métodos de dominio, comprobante automático, caso de uso completo
- API tests (9): registrar, completar (con y sin comprobante), historial, comprobante, fallido, reembolsar, flujo completo, restricción sesión no finalizada
- Uso de SQLite in-memory para aislar lógica y acelerar ejecución (override dinámico en settings)

**Flujo Simplificado Pago:**
1. Finalizar sesión → estado FINALIZADA con costo_total
2. Registrar pago (PENDIENTE)
3. Completar pago (COMPLETADO) y generar comprobante si falta
4. Consultar comprobante / historial
5. Opcional: marcar fallido o reembolsar según estado

**Beneficios del Diseño:**
- Extensible para nuevos métodos de pago (agregar enum + choices)
- Reembolsos auditables mediante estados explícitos
- Separación completa de lógica (dominio) y detalles ORM (infraestructura)
- Fácil reemplazo de repositorio (ej. servicio externo de facturación) implementando el puerto

---

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
