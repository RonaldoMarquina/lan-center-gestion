# Contexto del Proyecto - LAN Center Gestión

## Resumen de Configuración Completada

### Entorno de Desarrollo
- **Python**: 3.11.9 con entorno virtual en `.venv/`
- **Django**: 4.2.26 (Django REST Framework 3.14.*)
- **Base de Datos**: SQL Server (localhost:1433) con base de datos `lan_center` creada
- **ODBC**: Driver 18 for SQL Server configurado con TrustServerCertificate=yes
- **Docker Desktop**: Instalado para contenedorización y CI/CD

### Arquitectura Implementada
- **Patrón**: Clean Architecture + Hexagonal (Ports & Adapters)
- **Principios**: SOLID, Repository Pattern
- **Capas**:
  - `core/domain/` - Entidades de negocio puras
  - `core/application/` - Casos de uso y puertos (interfaces)
  - `infrastructure/` - Adaptadores (persistencia, servicios externos)
  - `presentation/api/` - Capa de API REST

### Dependencias Instaladas
- Django==4.2.*
- djangorestframework==3.14.*
- mssql-django==1.5.* (backend para SQL Server)
- pyodbc==5.1.*
- djangorestframework-simplejwt==5.3.* (autenticación JWT)
- python-decouple==3.8 (variables de entorno)
- drf-spectacular==0.26.* (documentación OpenAPI)
- gunicorn==21.2.* (servidor WSGI para producción)

### Configuración de Django
- **Variables de entorno**: Configuradas en `.env` (SECRET_KEY, DEBUG, DB credentials)
- **Autenticación**: JWT con tokens de 60 min (access) y 7 días (refresh)
- **Internacionalización**: es-pe, zona horaria America/Lima
- **Migraciones**: Ejecutadas (tablas de Django creadas en SQL Server)
- **Superusuario**: Creado para acceso al admin

### Endpoints Disponibles
- `/admin/` - Panel de administración Django
- `/api/auth/token/` - Obtener JWT (login)
- `/api/auth/token/refresh/` - Refrescar JWT
- `/api/docs/` - Documentación Swagger UI
- `/api/redoc/` - Documentación ReDoc
- `/api/schema/` - Schema OpenAPI

### Estado Git
- **Repositorio**: RonaldoMarquina/lan-center-gestion
- **Branch**: main
- **Último commit**: "feat(backend): configuracion base Django + DRF + SQL Server con arquitectura limpia hexagonal"
- **Archivos trackeados**: settings.py, urls.py, requirements.txt, .env.example, Contexto-del-proyecto.md

### Próximos Pasos Sugeridos
1. Implementar modelos de dominio (Usuario, Cabina, Reserva, Pago, Sesion)
2. Crear interfaces de repositorios (ports) en `core/application/ports/`
3. Implementar repositorios concretos (adapters) en `infrastructure/adapters/persistence/`
4. Desarrollar casos de uso en `core/application/use_cases/`
5. Crear serializers y ViewSets en `presentation/api/`
6. Escribir pruebas unitarias en `tests/`

---
## Descripción del silabus a respetar del curso
Unidad 1: Fundamentos avanzados de construcción y gestión del desarrollo
Unidad 2: Diseño de soluciones escalables con arquitectura limpia y patrones
Patrones de diseño
orientados a la reutilización
(Factory, Strategy, Adapter)
Arquitectura limpia y
hexagonal
Agentes y asistentes de
código con inteligencia
artificial
Unidad 3: Seguridad, resiliencia y desarrollo distribuido
Seguridad en APIs (.NET): OWASP,
JWT
Manejo de errores y patrones de
resiliencia (Retry, Circuit Breaker
con Polly)
Software distribuido y
comunicación entre servicios
Observabilidad en aplicaciones
distribuidas
## Requisitos Funcionales

N°,Requisito Funcional,Descripción
RF 01,Registro de Usuarios,"El sistema debe permitir el registro de nuevos usuarios (clientes y administradores), solicitando datos básicos como nombre, correo electrónico y contraseña."
RF 02,Inicio de Sesión Seguro,El sistema debe permitir a los usuarios iniciar sesión de forma segura utilizando su usuario y contraseña.
RF 03,Gestión de Roles y Permisos,"El sistema debe implementar un sistema de roles (Administrador, Usuario) para gestionar los permisos de acceso a las diferentes funcionalidades."
RF 04,Protección de Endpoints,"El sistema debe proteger las rutas y endpoints de la API, asegurando que solo los usuarios autenticados y autorizados puedan acceder a ellos."
RF 05,Cierre de Sesión,"El sistema debe permitir a los usuarios cerrar su sesión de forma segura, invalidando el token de acceso."
RF 06,Creación de Cabinas,"El sistema debe permitir al administrador crear (dar de alta) nuevas cabinas, especificando un identificador único y sus características."
RF 07,Modificación de Cabinas,El sistema debe permitir al administrador modificar la información de las cabinas existentes.
RF 08,Cambio de Estado Manual,"El sistema debe permitir al administrador cambiar el estado de una cabina manualmente (ej. ponerla ""en mantenimiento"" o ""desactivada"")."
RF 09,Eliminación de Cabinas,El sistema debe permitir al administrador eliminar cabinas que ya no están en servicio.
RF 10,Panel de Control en Tiempo Real,"El sistema debe mostrar al administrador un panel de control con la visualización en tiempo real del estado de todas las cabinas (Libre, Ocupada, Mantenimiento)."
RF 11,Reserva para Uso Inmediato,"El sistema debe permitir a los usuarios reservar una cabina para uso inmediato, seleccionando una de las que se encuentren disponibles."
RF 12,Reserva Anticipada,El sistema debe permitir a los usuarios realizar una reserva anticipada para una fecha y hora específicas.
RF 13,Control de Tiempo Automático,El sistema debe iniciar un contador de tiempo automáticamente cuando un usuario ocupe una cabina.
RF 14,Cálculo de Costo en Tiempo Real,El sistema debe calcular el costo total del servicio en tiempo real basándose en la duración del uso y la tarifa establecida.
RF 15,Extensión de Sesión,El sistema debe permitir a los usuarios extender la duración de su sesión si la cabina no tiene reservas posteriores.
RF 16,Finalización de Sesión,"El sistema debe finalizar la sesión de tiempo y actualizar el estado de la cabina a ""Libre"" una vez que el usuario termina y se registra el pago."
RF 17,Registro de Pago,"El sistema debe permitir al administrador registrar el pago de un servicio, ya sea en efectivo o mediante un método electrónico simulado."
RF 18,Historial de Pagos,El sistema debe generar un historial de pagos asociados a cada cliente.
RF 19,Comprobante de Pago,El sistema debe permitir la generación de un comprobante o factura simplificada por cada transacción completada.
RF 20,Reportes de Ingresos,El sistema debe generar reportes diarios y semanales sobre el total de ingresos.
RF 21,Estadísticas de Ocupación,El sistema debe generar estadísticas sobre las horas de mayor ocupación de las cabinas.
RF 22,Gráficos de Tasa de Ocupación,El sistema debe mostrar gráficos con la tasa de ocupación por cabina para identificar las más y menos utilizadas.
RF 23,Historial de Reservas y Uso,El sistema debe permitir al administrador visualizar un historial completo de reservas y sesiones de uso.
RF 24,Gestión de Datos de Usuarios,"El sistema debe permitir al administrador gestionar los datos de los usuarios registrados (ver, editar, eliminar)."
RF 25,Asignación/Cambio de Rol,El sistema debe permitir al administrador asignar o cambiar el rol de un usuario.
RF 26,Configuración General del Sistema,"El sistema debe contar con un panel de configuración general donde el administrador pueda definir parámetros del sistema, como las tarifas por hora."

N°,Requisito No Funcional,Descripción
RNF 01,Rendimiento de la API,El sistema debe tener un tiempo de respuesta para las peticiones API inferior a 500ms en condiciones de carga normal.
RNF 02,Concurrencia,El sistema debe ser capaz de manejar un mínimo de 50 sesiones de usuario concurrentes sin degradación del servicio.
RNF 03,Latencia de Interfaz,La actualización del estado de las cabinas en la interfaz del administrador debe reflejarse en menos de 2 segundos desde que ocurre el evento.
RNF 04,Seguridad de Contraseñas,Todas las contraseñas de los usuarios deben ser almacenadas en la base de datos utilizando un algoritmo de hashing robusto.
RNF 05,Cifrado de Comunicación,Toda la comunicación entre el cliente y el servidor debe ser cifrada utilizando el protocolo HTTPS.
RNF 06,Validación de Entradas,"El sistema debe implementar validación de entradas en la API para prevenir ataques comunes como Inyección SQL y Cross-Site Scripting (XSS), siguiendo las guías de OWASP."
RNF 07,Expiración de Tokens,Los tokens de autenticación (JWT) deben tener un tiempo de expiración corto y definido para mitigar el riesgo de robo de sesión.
RNF 08,Cumplimiento SOLID,El código fuente del backend debe adherirse estrictamente a los principios de diseño SOLID.
RNF 09,Arquitectura Limpia,"La estructura del proyecto debe seguir las capas definidas por la Arquitectura Limpia (Domain, Application, Infrastructure, Presentation)."
RNF 10,Cobertura de Pruebas,El sistema debe alcanzar una cobertura de código de pruebas unitarias de al menos el 80% para la lógica de negocio.
RNF 11,Estilo y Comentarios de Código,El código debe seguir las convenciones de estilo estándar del lenguaje de programación elegido (Python) y estar debidamente comentado en las secciones complejas.
RNF 12,Escalabilidad Horizontal,"La arquitectura del sistema debe ser modular para permitir el escalado horizontal, añadiendo nuevas instancias de los servicios en contenedores según la demanda."
RNF 13,Disponibilidad,El sistema debe tener una disponibilidad del 99.5% durante el horario de operación del LAN center.
RNF 14,Generación de Logs,"El sistema debe generar logs estructurados (ej. con Serilog) para todos los eventos importantes, errores y transacciones, facilitando la depuración y auditoría."
RNF 15,Métricas de Rendimiento,"El sistema debe exponer métricas clave de rendimiento (uso de CPU/memoria, latencia de la API) en un formato compatible con Prometheus."
RNF 16,Contenedorización Total,"Toda la aplicación, incluyendo la base de datos y los servicios de mensajería, debe estar completamente contenedorizada con Docker para garantizar la consistencia entre entornos."
RNF 17,Pipeline CI/CD,"El proceso de integración, pruebas y despliegue en el entorno de producción debe estar automatizado mediante un pipeline de CI/CD (ej. GitHub Actions)."
RNF 18,Usabilidad,"La interfaz de usuario debe ser intuitiva y fácil de usar, requiriendo una capacitación mínima para el personal administrativo."
RNF 19,Compatibilidad de Navegadores,"El sistema debe ser compatible con las últimas dos versiones de los navegadores web modernos (Google Chrome, Mozilla Firefox, Microsoft Edge)."

N°,Requisito Funcional,Caso de Uso
1,RF01: Permitir el registro de nuevos usuarios (clientes y administradores). ,CU01. Registrarse en el Sistema 
2,RF02: Permitir a los usuarios iniciar sesión de forma segura. ,CU02. Autenticar Usuario 
3,RF04: Proteger las rutas y endpoints de la API con autorización. ,CU02. Autenticar Usuario 
4,RF05: Permitir a los usuarios cerrar su sesión de forma segura. ,CU02. Autenticar Usuario 
5,RF06: Permitir al administrador crear (dar de alta) nuevas cabinas. ,CU03. Gestionar Cabinas 
6,RF07: Permitir al administrador modificar la información de las cabinas. ,CU03. Gestionar Cabinas 
7,RF08: Permitir al administrador cambiar el estado de una cabina manualmente. ,CU03. Gestionar Cabinas 
8,RF09: Permitir al administrador eliminar cabinas del sistema. ,CU03. Gestionar Cabinas 
9,RF10: Mostrar al administrador un panel con el estado en tiempo real de las cabinas. ,CU03. Gestionar Cabinas 
10,RF11: Permitir a los usuarios reservar una cabina para uso inmediato. ,CU04. Gestionar Reservas y Sesiones de Uso 
11,RF12: Permitir a los usuarios realizar una reserva anticipada. ,CU04. Gestionar Reservas y Sesiones de Uso 
12,RF13: Iniciar un contador de tiempo al ocupar una cabina. ,CU04. Gestionar Reservas y Sesiones de Uso 
13,RF15: Permitir a los usuarios extender la duración de su sesión. ,CU04. Gestionar Reservas y Sesiones de Uso 
14,RF16: Finalizar la sesión de tiempo y actualizar el estado de la cabina. ,CU04. Gestionar Reservas y Sesiones de Uso 
15,RF14: Calcular el costo del servicio en tiempo real según la duración. ,CU05. Procesar Pago de Servicio 
16,RF17: Permitir al administrador registrar el pago de un servicio. ,CU05. Procesar Pago de Servicio 
17,RF18: Generar un historial de pagos asociados a cada cliente. ,CU05. Procesar Pago de Servicio 
18,RF19: Permitir la generación de un comprobante o factura simplificada. ,CU05. Procesar Pago de Servicio 
19,RF20: Generar reportes diarios y semanales sobre el total de ingresos. ,CU06. Consultar Reportes y Estadísticas 
20,RF21: Generar estadísticas sobre las horas de mayor ocupación. ,CU06. Consultar Reportes y Estadísticas 
21,RF22: Mostrar gráficos con la tasa de ocupación por cabina. ,CU06. Consultar Reportes y Estadísticas 
22,RF23: Permitir al administrador visualizar un historial de reservas y sesiones. ,CU06. Consultar Reportes y Estadísticas 
23,"RF03: Implementar un sistema de roles (Administrador, Usuario). ",CU07. Administrar Usuarios y Roles 
24,RF24: Permitir al administrador gestionar los datos de los usuarios registrados. ,CU07. Administrar Usuarios y Roles 
25,RF25: Permitir al administrador asignar o cambiar el rol de un usuario. ,CU07. Administrar Usuarios y Roles 
26,RF26: Contar con un panel para configurar parámetros generales del sistema. ,CU08. Configurar Parámetros del Sistema 

N°,Caso de Uso,Actores,Descripción y Flujos
01,CU01. Registrarse en el Sistema,Visitante (Nuevo Usuario) ,"Flujo Normal: Un nuevo usuario accede al sistema y selecciona la opción ""Registrarse"". Completa el formulario con sus datos (nombre, correo electrónico, usuario, contraseña). El sistema valida los datos, crea la nueva cuenta con el rol de ""Usuario"" y le notifica que el registro fue exitoso. Flujo Alterno: Si el correo electrónico ingresado ya existe, el sistema muestra el mensaje: ""El correo electrónico ya se encuentra registrado"". Si la contraseña no cumple con los requisitos de seguridad (ej. mínimo 8 caracteres, una mayúscula), el sistema muestra un mensaje de advertencia. Si algún campo obligatorio está vacío, el sistema lo indicará."
02,CU02. Autenticar Usuario,"Usuario (Cliente, Administrador) ","Flujo Normal: El usuario ingresa su usuario y contraseña en el formulario de inicio de sesión. El sistema valida las credenciales. Si son correctas, el sistema genera un token de sesión (JWT) y redirige al usuario a su panel correspondiente según su rol. Flujo Alterno: Si las credenciales son incorrectas, el sistema muestra el mensaje: ""Correo o contraseña incorrectos. Intente nuevamente"". Si el usuario intenta acceder a una ruta protegida sin haber iniciado sesión, es redirigido a la página de login."
03,CU03. Gestionar Cabinas,Administrador ,"Flujo Normal: El administrador accede al panel de ""Gestión de Cabinas"", donde visualiza un listado de todas las cabinas y su estado actual (Libre, Ocupada, Mantenimiento). Para crear una cabina, selecciona ""Añadir"", completa la información y guarda. Para modificar una cabina, la selecciona del listado, edita sus datos y guarda los cambios. Para cambiar el estado, selecciona una cabina y elige el nuevo estado (ej. ""Poner en Mantenimiento""). Flujo Alterno: Si el administrador intenta guardar una nueva cabina con un identificador que ya existe, el sistema mostrará un error. El sistema no permitirá eliminar una cabina que se encuentre en estado ""Ocupada""."
04,CU04. Gestionar Reservas y Sesiones de Uso,"Usuario (Cliente), Administrador ","Flujo Normal: El cliente inicia sesión y ve las cabinas disponibles. Selecciona una cabina libre para iniciar una sesión de uso inmediato. El sistema cambia el estado de la cabina a ""Ocupada"" y comienza a contabilizar el tiempo y el costo. Al finalizar, el cliente notifica al administrador para terminar la sesión. El sistema detiene el contador y calcula el monto final a pagar. Flujo Alterno: Si un cliente intenta reservar una cabina que justo en ese momento es ocupada por otro, el sistema le notificará que la cabina ya no está disponible y deberá elegir otra."
05,CU05. Procesar Pago de Servicio,Administrador ,"Flujo Normal: Al finalizar una sesión de uso (desde CU04), el sistema muestra al administrador el monto total a pagar por el cliente. El administrador confirma la recepción del pago. El sistema registra la transacción, la asocia al historial del cliente y genera un comprobante digital. Automáticamente, el estado de la cabina correspondiente se actualiza a ""Libre"". Flujo Alterno: Si hay un error al intentar registrar el pago, el sistema mantendrá la sesión como ""Pendiente de pago"" y no liberará la cabina hasta que se resuelva."
06,CU06. Consultar Reportes y Estadísticas,Administrador ,"Flujo Normal: El administrador accede a la sección de ""Reportes"". Selecciona el tipo de reporte que desea visualizar (ej. Ingresos por día, Horas de mayor ocupación, Uso por cabina). Puede filtrar los resultados por un rango de fechas. El sistema procesa la información y la presenta en formato de tablas y/o gráficos. Flujo Alterno: Si no existen datos para el filtro seleccionado (ej. un día sin actividad), el sistema mostrará un mensaje indicando ""No hay datos para mostrar en el período seleccionado""."
07,CU07. Administrar Usuarios y Roles,Administrador ,"Flujo Normal: El administrador accede al panel de ""Gestión de Usuarios"". Visualiza una lista de todos los usuarios registrados en el sistema. Puede seleccionar un usuario para editar su información personal o para cambiar su rol (de ""Usuario"" a ""Administrador"" o viceversa). Guarda los cambios, que se aplican de inmediato. Flujo Alterno: El sistema impedirá que el único administrador del sistema se elimine a sí mismo o cambie su propio rol a ""Usuario""."
08,CU08. Configurar Parámetros del Sistema,Administrador ,"Flujo Normal: El administrador accede a la sección de ""Configuración"". Modifica los valores de los parámetros del sistema, como la tarifa por hora de uso de las cabinas. Guarda la nueva configuración. El sistema utilizará estos nuevos valores para todos los cálculos futuros (ej. nuevas sesiones iniciadas después del cambio). Flujo Alterno: Si el administrador ingresa un valor no válido (ej. una tarifa negativa o no numérica), el sistema mostrará un error de validación y no permitirá guardar los cambios."