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

## Redes y Base de Datos RDS (Capa Gold)

Para la capa de consumo analítico (Gold), se despliega una instancia relacional PostgreSQL con un Security Group que restringe el acceso exclusivamente a la IP local del desarrollador.

**Comandos de despliegue mediante AWS CLI:**

```bash
# Creación del Security Group
aws ec2 create-security-group \
    --group-name rds-etl-sg \
    --description "Acceso a RDS Capa Gold desde IP local" \
    --vpc-id TU_VPC_ID

# Regla de entrada - Restringida a IP local
aws ec2 authorize-security-group-ingress \
    --group-id TU_SG_ID \
    --protocol tcp \
    --port 5432 \
    --cidr TU_IP/32

# Lanzamiento de la BD
aws rds create-db-instance \
    --db-instance-identifier datalake-gold-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username postgres \
    --master-user-password TU_PASSWORD \
    --allocated-storage 20 \
    --vpc-security-group-ids TU_SG_ID \
    --publicly-accessible \
    --no-multi-az
```
