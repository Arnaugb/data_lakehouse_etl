# Infraestructura AWS - Data Lakehouse ETL Pipeline

Este documento detalla la infraestructura necesaria en Amazon Web Services (AWS) para ejecutar el pipeline.

## Configuración de IAM

Para mantener el principio de menor privilegio y evitar exponer la cuenta root, se requiere un usuario dedicado:

- **Nombre de usuario:** `etl-pipeline-user`
- **Tipo de acceso:** Exclusivamente programático (Access Key ID & Secret Access Key). Sin acceso a la consola de administración web.
- **Políticas:** `AmazonS3FullAccess`

## 2. Almacenamiento S3

Los buckets actúan como las capas Bronze (datos crudos) y Silver (datos limpios y particionados en formato Parquet). Se despliegan en la región `eu-west-1` (Irlanda).

**Comandos de despliegue mediante AWS CLI:**

```bash
# Creación del bucket para la Capa Bronze
aws s3api create-bucket \
    --bucket arnau-datalake-bronze-12345 \
    --region eu-west-1 \
    --create-bucket-configuration LocationConstraint=eu-west-1

# Creación del bucket para la Capa Silver
aws s3api create-bucket \
    --bucket arnau-datalake-silver-12345 \
    --region eu-west-1 \
    --create-bucket-configuration LocationConstraint=eu-west-1
```
