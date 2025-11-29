#!/usr/bin/env bash
set -e

### VARIABLES BÁSICAS
export PROJECT_ID="techo-chile"
export REGION_PRIMARY="southamerica-west1"      # Santiago
export REGION_DR="southamerica-east1"          # São Paulo

export SERVICE_NAME="techo-django"
export DB_PRIMARY="techo-sql-primary"
export DB_REPLICA="techo-sql-replica"
export ARTIFACT_REPO="django-repo"

export DB_NAME="django_db"
export DB_USER="django_user"
export DB_PASSWORD="Internet3108"              # luego podemos pasarlo a Secret Manager

gcloud config set project "$PROJECT_ID"

echo "== 1) Habilitar APIs necesarias =="
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  compute.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com

echo "== 2) Crear repo de Artifact Registry =="
gcloud artifacts repositories create "$ARTIFACT_REPO" \
  --repository-format=docker \
  --location="$REGION_PRIMARY" \
  --description="Repo Django para Techo" || echo "Repo puede que ya exista, continuando..."

export IMAGE="$REGION_PRIMARY-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REPO/django-app"

echo "== 3) Construir y subir la imagen Docker con Cloud Build =="
gcloud builds submit --tag "$IMAGE" .

echo "== 4) Crear instancia primaria de Cloud SQL (Postgres) HA con PITR =="
gcloud sql instances create "$DB_PRIMARY" \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-7680 \
  --region="$REGION_PRIMARY" \
  --availability-type=REGIONAL \
  --storage-auto-increase \
  --backup-start-time=03:00 \
  --enable-point-in-time-recovery \
  --storage-type=SSD

echo "== 4.1) Crear BD y usuario para Django =="
gcloud sql databases create "$DB_NAME" --instance="$DB_PRIMARY"

gcloud sql users create "$DB_USER" \
  --instance="$DB_PRIMARY" \
  --password="$DB_PASSWORD"

# Nombre de conexión para usar sockets en Cloud Run
export INSTANCE_CONN_PRIMARY="$PROJECT_ID:$REGION_PRIMARY:$DB_PRIMARY"

echo "== 4.2) Crear réplica en región DR =="
gcloud sql instances create "$DB_REPLICA" \
  --master-instance-name="$DB_PRIMARY" \
  --region="$REGION_DR"

echo "== 5) Desplegar Cloud Run en región primaria (activa) =="
gcloud run deploy "$SERVICE_NAME" \
  --image="$IMAGE" \
  --region="$REGION_PRIMARY" \
  --platform=managed \
  --allow-unauthenticated \
  --min-instances=2 \
  --max-instances=50 \
  --cpu=2 \
  --memory=2Gi \
  --add-cloudsql-instances="$INSTANCE_CONN_PRIMARY" \
  --set-env-vars="DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,DB_HOST=/cloudsql/$INSTANCE_CONN_PRIMARY,DB_PORT=5432"

echo "== 6) Desplegar Cloud Run en región DR (pasiva, listo para failover) =="
gcloud run deploy "$SERVICE_NAME" \
  --image="$IMAGE" \
  --region="$REGION_DR" \
  --platform=managed \
  --allow-unauthenticated \
  --min-instances=1 \
  --max-instances=30 \
  --cpu=2 \
  --memory=2Gi \
  --add-cloudsql-instances="$INSTANCE_CONN_PRIMARY" \
  --set-env-vars="DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,DB_HOST=/cloudsql/$INSTANCE_CONN_PRIMARY,DB_PORT=5432"

echo "== 7) Crear NEGs serverless para cada región =="
gcloud compute network-endpoint-groups create cr-techo-primary-neg \
  --region="$REGION_PRIMARY" \
  --network-endpoint-type=serverless \
  --cloud-run-service="$SERVICE_NAME"

gcloud compute network-endpoint-groups create cr-techo-dr-neg \
  --region="$REGION_DR" \
  --network-endpoint-type=serverless \
  --cloud-run-service="$SERVICE_NAME"

echo "== 8) Backend service HTTP global con Cloud CDN activado =="
gcloud compute backend-services create techo-backend \
  --global \
  --protocol=HTTP \
  --enable-cdn

# Activa-pasiva: sólo backend primario. El de DR lo añadimos cuando quieras failover.
gcloud compute backend-services add-backend techo-backend \
  --global \
  --network-endpoint-group=cr-techo-primary-neg \
  --network-endpoint-group-region="$REGION_PRIMARY"

echo "== 9) IP global para el Load Balancer HTTP =="
gcloud compute addresses create techo-ip --global || echo "IP puede que ya exista"
export DJANGO_IP=$(gcloud compute addresses describe techo-ip --global --format="value(address)")
echo "IP del LB (anótala): $DJANGO_IP"

echo "== 10) Crear URL map, proxy HTTP y regla de reenvío =="
gcloud compute url-maps create techo-http-map \
  --default-backend-service=techo-backend

gcloud compute target-http-proxies create techo-http-proxy \
  --url-map=techo-http-map

gcloud compute forwarding-rules create techo-http-lb \
  --global \
  --target-http-proxy=techo-http-proxy \
  --ports=80 \
  --address=techo-ip

echo "== 11) Cloud Armor 'permitir todo' (luego afinamos reglas) =="
gcloud compute security-policies create techo-armor-policy \
  --description="Policy inicial, permite todo" || echo "Policy puede existir"

gcloud compute backend-services update techo-backend \
  --global \
  --security-policy=techo-armor-policy

echo "=========================================="
echo "Arquitectura desplegada."
echo "Accede a la app en:  http://$DJANGO_IP"
echo "Luego podemos:"
echo "- Añadir SSL y dominio cuando tengas uno."
echo "- Endurecer Cloud Armor (WAF, geofiltros, rate limiting)."
echo "- Definir procedimiento de failover a la región DR."
echo "=========================================="
