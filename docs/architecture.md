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


