# Cloud-Native Data Lakehouse ETL

Pipeline ETL diseñado para ingerir, transformar y agregar telemetría de entrenamientos deportivos (natación, ciclismo, carrera) aplicando el modelo de arquitectura Medallion (Bronze, Silver, Gold).

## Stack Tecnológico

- **Lenguaje:** Python 3.10+
- **Procesamiento de Datos:** Pandas, Pydantic
- **AWS Cloud:** S3, RDS (PostgreSQL), IAM, EC2 Security Groups
- **Librerías:** Boto3, psycopg2, requests

## Arquitectura del Pipeline

El flujo de datos se divide en tres capas lógicas ejecutadas de forma secuencial:

### 1. Capa Bronze

- **Ingesta Serverless:** Los clientes suben los archivos CSV directamente a S3 mediante **Presigned URLs** generadas dinámicamente con Boto3 (SigV4). Esto evita saturar la memoria del backend durante la transferencia.

### 2. Capa Silver

- **Procesamiento In-Memory:** El archivo CSV se lee desde S3 directamente a la RAM mediante `io.BytesIO`.
- **Limpieza y Formato:** Estandarización de nombres de columnas y parseo de marcas de tiempo con Pandas.
- **Almacenamiento Columnar:** Los datos se convierten a formato **Parquet** (PyArrow) y se guardan en S3 aplicando particionamiento lógico `year=YYYY/month=MM/day=DD`.

### 3. Capa Gold

- **Transformación:** Descarga del Parquet desde Silver, cálculo de inicios de semana y agregación de métricas de negocio. En este caso es el volumen total y frecuencia cardíaca media por usuario y semana.
- **Validación de Contratos:** Cada fila agregada se valida estrictamente contra un esquema de **Pydantic**.
- **Carga Transaccional:** Inserción en lote en PostgreSQL (AWS RDS). Se utiliza lógica **Upsert** (`ON CONFLICT DO UPDATE`) para garantizar la idempotencia: el pipeline puede ejecutarse múltiples veces sin generar registros duplicados ni corromper el histórico. Si un lote falla, se ejecuta un `ROLLBACK` completo.

## Puntos Técnicos Destacados

- **Seguridad de Red y Credenciales:** Conexiones a la base de datos protegidas mediante reglas de Ingress en Security Groups. Gestión de credenciales locales aislada mediante `.env`.
- **Idempotencia:** Gracias a las restricciones `PRIMARY KEY` y el manejo de conflictos en SQL, la integridad del Data Warehouse analítico está garantizada frente a reejecuciones accidentales.
- **Trazabilidad:** Sistema de logging integrado para monitorizar las transiciones entre capas, caídas de red o fallos de validación en tiempo real.

## Ejecución Local

1. Clonar el repositorio.
2. Crear un entorno virtual e instalar las dependencias: `pip install -r requirements.txt`.
3. Configurar el archivo `.env` con las credenciales de AWS y los datos de conexión al endpoint de RDS.
4. Ejecutar el orquestador:
   ```bash
   python -m src.pipeline
   ```
