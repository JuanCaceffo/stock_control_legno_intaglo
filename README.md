# Legno Intaglo Stock API

API para gestión de inventario de stock desarrollada con FastAPI y PostgreSQL.

## Características

- **Framework**: FastAPI
- **Base de datos**: PostgreSQL
- **ORM**: SQLModel
- **Contenedores**: Docker & Docker Compose
- **Arquitectura**: Domain-Driven Design (DDD) con capas separadas

## Estructura del Proyecto

```
legno_intaglo/
├── src/
│   ├── config/
│   │   └── database.py          # Configuración de base de datos
│   ├── controller/
│   │   └── stock_controller.py  # Endpoints API
│   ├── domain/
│   │   └── stock.py             # Objetos de dominio y validaciones
│   ├── entities/
│   │   └── stock.py             # Entidades SQLModel (tablas)
│   ├── schemas/
│   │   └── stock.py             # Modelos Pydantic (requests/responses)
│   ├── services/
│   │   └── stock_service.py     # Lógica de negocio
│   └── main.py                  # Aplicación FastAPI
├── .env                         # Variables de entorno
├── Dockerfile                   # Configuración Docker para la app
├── docker-compose.yml           # Orquestación de contenedores
├── requirements.txt             # Dependencias Python
└── README.md                    # Este archivo
```

## Requisitos

- Docker y Docker Compose
- Python 3.11+ (para desarrollo local sin Docker)

## Instalación y Ejecución con Docker

### 1. Clonar el repositorio

```bash
cd /home/juan/Documents/projects/legno_intaglo
```

### 2. Construir y levantar los contenedores

```bash
docker-compose up --build
```

Esto iniciará:
- **PostgreSQL** en el puerto 5432
- **API FastAPI** en el puerto 8000

### 3. Verificar que la API está funcionando

Abrir en el navegador:
- API: http://localhost:8000
- Documentación interactiva (Swagger UI): http://localhost:8000/docs
- Documentación alternativa (ReDoc): http://localhost:8000/redoc

## API Endpoints

### POST /stocks/

Crear un nuevo registro de stock.

**Request Body:**
```json
{
  "item_name": "Madera Roble",
  "sku": "ROBLE-001",
  "quantity": 100.5,
  "unit": "m",
  "category": "raw_material",
  "min_stock_alert": 20.0
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "item_name": "Madera Roble",
  "sku": "ROBLE-001",
  "quantity": 100.5,
  "unit": "m",
  "category": "raw_material",
  "min_stock_alert": 20.0,
  "status": "low",
  "created_at": "2025-01-01T12:00:00.000000",
  "updated_at": "2025-01-01T12:00:00.000000"
}
```

**Campos disponibles:**

- `item_name` (string, requerido): Nombre del artículo
- `sku` (string, requerido): Identificador único de stock
- `quantity` (float, requerido, >= 0): Cantidad en stock
- `unit` (enum, requerido): Unidad de medida
  - `m` (meters/metros)
  - `pcs` (pieces/piezas)
  - `kg` (kilograms/kilogramos)
  - `l` (liters/litros)
  - `units` (unidades)
  - `boxes` (cajas)
  - `pallets` (palets)
- `category` (enum, requerido): Categoría del producto
  - `raw_material` (material_crudo)
  - `finished_product` (producto_terminado)
  - `packaging` (empaque)
  - `tools` (herramientas)
  - `spare_parts` (repuestos)
  - `consumables` (consumibles)
  - `electronics` (electrónica)
  - `hardware` (hardware)
- `min_stock_alert` (float, opcional, >= 0): Umbral mínimo de alerta de stock

**Validaciones:**
- SKU no puede estar vacío
- Cantidad no puede ser negativa
- `min_stock_alert` no puede ser negativo
- `min_stock_alert` no puede exceder la cantidad actual
- SKU debe ser único (no se permiten duplicados)

**Errores posibles:**
- `400 Bad Request`: Validación fallida o SKU duplicado
- `500 Internal Server Error`: Error del servidor

## Ejecución sin Docker (desarrollo local)

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env  # Si existe .env.example
# Editar .env con la configuración de la base de datos
```

### 3. Tener PostgreSQL corriendo localmente

```bash
# Ejemplo con Docker
docker run -d \
  --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=legno_intaglo \
  -p 5432:5432 \
  postgres:15-alpine
```

### 4. Ejecutar la aplicación

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing con curl

```bash
# Crear un stock
curl -X POST "http://localhost:8000/stocks/" \
  -H "Content-Type: application/json" \
  -d '{
    "item_name": "Tornillo Acero",
    "sku": "TORN-001",
    "quantity": 500,
    "unit": "units",
    "category": "hardware",
    "min_stock_alert": 100
  }'
```

## Notas de Implementación

### Patrón de Diseño
Se utiliza una arquitectura por capas con Domain-Driven Design (DDD):

1. **Domain** (`src/domain/`): Contiene la lógica de negocio y validaciones
2. **Entities** (`src/entities/`): Entidades de base de datos (SQLModel)
3. **Schemas** (`src/schemas/`): Modelos de validación (Pydantic)
4. **Services** (`src/services/`): Capa de servicios que orquesta la lógica
5. **Controller** (`src/controller/`): Endpoints de la API (FastAPI)
6. **Config** (`src/config/`): Configuración de la base de datos

### Validaciones
- Las validaciones de dominio se realizan en `Stock.__post_init__()`
- Las validaciones de request se realizan con Pydantic en `StockCreate`
- Se verifica unicidad de SKU en la base de datos

### Base de Datos
- Las tablas se crean automáticamente al iniciar la aplicación (`init_db()`)
- Se utiliza SQLModel sobre SQLAlchemy
- PostgreSQL en contenedor Docker

## Desarrollo

### Agregar nuevas funcionalidades

1. Crear modelos en `src/domain/` si es necesario
2. Crear entidades en `src/entities/` para tablas
3. Crear schemas en `src/schemas/` para validación
4. Implementar lógica en `src/services/`
5. Crear endpoints en `src/controller/`

### Ejecutar tests

```bash
pytest
```

## Producción

Para despliegue en producción:

1. Configurar variables de entorno apropiadas
2. Usar Docker Compose con archivos de override
3. Configurar backups de PostgreSQL
4. Habilitar logging estructurado
5. Configurar CORS según necesidades
6. Agregar autenticación si es necesaria

## Licencia

[Especificar licencia]

## Contacto

[Información de contacto]
