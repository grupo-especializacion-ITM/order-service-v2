# Microservicio de Pedidos para Restaurantes

Este proyecto implementa un microservicio para la gestión de pedidos en un sistema de restaurantes, utilizando arquitectura hexagonal (puertos y adaptadores).

## Tecnologías utilizadas

- Python 3.11+
- FastAPI: Framework web de alto rendimiento
- SQLAlchemy: ORM para la interacción con la base de datos
- Alembic: Herramienta para migraciones de base de datos
- Kafka: Comunicación asíncrona entre microservicios
- PostgreSQL: Base de datos relacional

## Arquitectura Hexagonal

El proyecto sigue los principios de la arquitectura hexagonal (puertos y adaptadores):

### Capa de Dominio 

Contiene:
- Entidades (Order, Customer, OrderItem)
- Objetos de valor (DeliveryAddress, OrderTotal)
- Agregados (OrderAggregate)
- Puertos de entrada/salida para definir las interfaces

### Capa de Aplicación

Contiene:
- Servicios que implementan los puertos de entrada
- DTOs para la comunicación entre capas
- Eventos de dominio

### Capa de Infraestructura

Contiene:
- Adaptadores de entrada (API REST con FastAPI)
- Adaptadores de salida (Repositorio SQL, Servicio de Inventario, Publisher de Kafka)
- Configuración de la aplicación

## Estructura del proyecto

```
order_service/
├── src/
│   ├── domain/             # Capa de dominio
│   │   ├── entities/       # Entidades del dominio
│   │   ├── value_objects/  # Objetos de valor
│   │   ├── aggregates/     # Agregados
│   │   ├── exceptions/     # Excepciones del dominio
│   │   └── ports/          # Puertos (entrada/salida)
│   ├── application/        # Capa de aplicación
│   │   ├── dtos/           # Objetos de transferencia de datos
│   │   ├── services/       # Servicios de aplicación
│   │   ├── mappers/        # Mapeadores entre entidades y DTOs
│   │   └── events/         # Eventos de dominio
│   └── infrastructure/     # Capa de infraestructura
│       ├── adapters/       # Adaptadores (entrada/salida)
│       ├── db/             # Configuración de base de datos y migraciones
│       └── config/         # Configuraciones
├── tests/                  # Pruebas unitarias e integración
├── alembic.ini             # Configuración de Alembic
└── main.py                 # Punto de entrada de la aplicación
```

## Configuración del entorno

1. Crear un archivo `.env` en la raíz del proyecto con la siguiente configuración:

```
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/orders_db
DB_ECHO=True
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
INVENTORY_SERVICE_URL=http://inventory-service:8000
DEBUG=True
```

## Migraciones de base de datos

Para ejecutar las migraciones de base de datos:

```bash
# Crear una nueva migración
alembic revision --autogenerate -m "descripción_de_la_migración"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1
```

## Ejecución de la aplicación

### Modo desarrollo

```bash
uvicorn main:app --reload
```

### Con Docker

```bash
docker build -t order-service .
docker run -p 8000:8000 --env-file .env order-service
```

## API Endpoints

- `POST /api/v1/orders`: Crear un nuevo pedido
- `GET /api/v1/orders/{order_id}`: Obtener un pedido por ID
- `GET /api/v1/orders?customer_id={customer_id}`: Obtener pedidos de un cliente
- `PATCH /api/v1/orders/{order_id}/status`: Actualizar estado de un pedido
- `POST /api/v1/orders/{order_id}/confirm`: Confirmar un pedido
- `POST /api/v1/orders/{order_id}/cancel`: Cancelar un pedido
- `POST /api/v1/orders/{order_id}/items`: Añadir un ítem a un pedido
- `DELETE /api/v1/orders/{order_id}/items/{item_id}`: Eliminar un ítem de un pedido

## Eventos

El servicio publica los siguientes eventos en Kafka:

- `order.created`: Cuando se crea un nuevo pedido
- `order.confirmed`: Cuando se confirma un pedido
- `order.cancelled`: Cuando se cancela un pedido
- `order.status_updated`: Cuando cambia el estado de un pedido