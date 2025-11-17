# LAN Center - Sistema de Gestión

## Descripción

Sistema de gestión para centros de cómputo (LAN centers) desarrollado con arquitectura hexagonal (puertos y adaptadores), implementado con Django y Django REST Framework.

## Características

- Gestión de cabinas de computadoras
- Sistema de reservas
- Procesamiento de pagos
- Gestión de usuarios
- API REST completa

## Arquitectura

El proyecto sigue los principios de la arquitectura hexagonal:

- **Domain**: Lógica de negocio pura (entidades y reglas)
- **Application**: Casos de uso y servicios de aplicación
- **Infrastructure**: Implementaciones concretas (base de datos, servicios externos)
- **Presentation**: API REST (endpoints y serializadores)

## Requisitos

- Python 3.11+
- Django 4.2+
- Django REST Framework
- SQL Server (o PostgreSQL para desarrollo)
- Docker & Docker Compose

## Instalación

### Con Docker (Recomendado)

```bash
docker-compose up -d
```

### Manual

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r backend/requirements.txt
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
```

4. Ejecutar migraciones:
```bash
cd backend
python manage.py migrate
```

5. Iniciar servidor:
```bash
python manage.py runserver
```

## Estructura del Proyecto

```
lan-center-gestion/
├── backend/
│   ├── app/                    # Configuración Django
│   ├── core/                   # Dominio y Aplicación
│   ├── infrastructure/         # Persistencia y servicios externos
│   ├── presentation/           # API REST
│   └── tests/                  # Pruebas
├── docs/                       # Documentación
└── docker-compose.yml          # Orquestación de contenedores
```

## Pruebas

```bash
cd backend
python manage.py test
```

## Documentación

La documentación completa está disponible en el directorio `docs/`.

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto es privado y está protegido por derechos de autor.

## Contacto

Proyecto: lan-center-gestion
