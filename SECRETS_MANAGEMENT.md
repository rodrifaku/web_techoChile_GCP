# Gestión de Secretos - Techo Chile

## Secret Manager: `db-password`

### Estado Actual de Versiones

| Versión | Estado  | Fecha Creación       | En Uso | Notas                                    |
|---------|---------|----------------------|--------|------------------------------------------|
| 7       | enabled | 2025-12-01 13:29:53 | ✅ SÍ  | **VERSIÓN ACTIVA** - Contraseña limpia   |
| 6       | enabled | 2025-12-01 13:29:28 | ❌ NO  | Contraseña con saltos de línea           |
| 5       | enabled | 2025-12-01 13:27:29 | ❌ NO  | Contraseña con saltos de línea           |
| 4       | enabled | 2025-12-01 13:03:10 | ❌ NO  | Contraseña con saltos de línea           |
| 3       | enabled | 2025-12-01 12:08:02 | ❌ NO  | Contraseña con saltos de línea           |
| 2       | enabled | 2025-12-01 06:22:33 | ❌ NO  | Contraseña con saltos de línea           |
| 1       | enabled | 2025-12-01 05:11:02 | ❌ NO  | Versión inicial                          |

### Servicios y Versiones Utilizadas

| Servicio                    | Región             | Versión Secret | Estado    |
|-----------------------------|--------------------|----------------|-----------|
| techo-django (Cloud Run)    | southamerica-west1 | **7**          | ✅ Correcto |
| techo-django (Cloud Run)    | southamerica-east1 | **7**          | ✅ Correcto |
| django-migrate (Job)        | southamerica-west1 | **7**          | ✅ Correcto |
| django-create-superuser (Job)| southamerica-west1 | **latest**     | ⚠️ Usar v7  |

### ⚠️ Problema Identificado

El job `django-create-superuser` está configurado con `key: 'latest'` en lugar de `key: '7'`. Esto puede causar problemas si se crea una nueva versión del secret.

**Corrección recomendada:**
```bash
gcloud run jobs update django-create-superuser \
  --region=southamerica-west1 \
  --project=techo-chile \
  --update-secrets=DB_PASSWORD=db-password:7 \
  --update-secrets=DJANGO_SUPERUSER_PASSWORD=db-password:7
```

### Contraseña Actual (v7)

- **Valor**: `DjangoUser2024Pass` (18 caracteres, sin espacios ni saltos de línea)
- **Usuario DB**: `django_user`
- **Base de datos**: `django_db`
- **Instancias SQL**:
  - Primary (west1): `techo-chile:southamerica-west1:techo-sql-primary`
  - Replica (east1): `techo-chile:southamerica-east1:techo-sql-replica`

### Plan de Limpieza de Versiones Antiguas

Las versiones 1-6 contienen contraseñas con formato incorrecto (saltos de línea) y ya no se utilizan.

**Comandos para deshabilitar versiones antiguas:**

```bash
# Deshabilitar versión 1
gcloud secrets versions disable 1 --secret=db-password --project=techo-chile

# Deshabilitar versión 2
gcloud secrets versions disable 2 --secret=db-password --project=techo-chile

# Deshabilitar versión 3
gcloud secrets versions disable 3 --secret=db-password --project=techo-chile

# Deshabilitar versión 4
gcloud secrets versions disable 4 --secret=db-password --project=techo-chile

# Deshabilitar versión 5
gcloud secrets versions disable 5 --secret=db-password --project=techo-chile

# Deshabilitar versión 6
gcloud secrets versions disable 6 --secret=db-password --project=techo-chile
```

**O deshabilitar todas las versiones antiguas de una vez:**

```bash
for version in 1 2 3 4 5 6; do
  gcloud secrets versions disable $version --secret=db-password --project=techo-chile
done
```

### Plan de Rotación de Contraseñas

#### Frecuencia Recomendada
- **Producción**: Cada 90 días
- **Próxima rotación sugerida**: 1 de marzo de 2026

#### Procedimiento de Rotación

1. **Generar nueva contraseña segura:**
   ```bash
   # Generar contraseña de 24 caracteres
   openssl rand -base64 24 | tr -d '\n' | head -c 24
   ```

2. **Crear nueva versión del secret:**
   ```bash
   echo -n "NUEVA_CONTRASEÑA" | gcloud secrets versions add db-password \
     --data-file=- \
     --project=techo-chile
   ```

3. **Actualizar contraseña en Cloud SQL:**
   ```bash
   gcloud sql users set-password django_user \
     --instance=techo-sql-primary \
     --password="NUEVA_CONTRASEÑA" \
     --project=techo-chile
   ```

4. **Actualizar servicios Cloud Run (ambas regiones):**
   ```bash
   # West1
   gcloud run services update techo-django \
     --region=southamerica-west1 \
     --update-secrets=DB_PASSWORD=db-password:8 \
     --project=techo-chile
   
   # East1
   gcloud run services update techo-django \
     --region=southamerica-east1 \
     --update-secrets=DB_PASSWORD=db-password:8 \
     --project=techo-chile
   ```

5. **Actualizar jobs:**
   ```bash
   # django-migrate
   gcloud run jobs update django-migrate \
     --region=southamerica-west1 \
     --update-secrets=DB_PASSWORD=db-password:8 \
     --project=techo-chile
   
   # django-create-superuser
   gcloud run jobs update django-create-superuser \
     --region=southamerica-west1 \
     --update-secrets=DB_PASSWORD=db-password:8 \
     --update-secrets=DJANGO_SUPERUSER_PASSWORD=db-password:8 \
     --project=techo-chile
   ```

6. **Verificar conectividad:**
   ```bash
   # Verificar logs en west1
   gcloud run services logs read techo-django \
     --region=southamerica-west1 \
     --limit=20 | Select-String -Pattern "Error|DB"
   
   # Probar endpoint
   curl https://techo-django-47670800654.southamerica-west1.run.app/
   ```

7. **Deshabilitar versión antigua (después de 24-48 horas de pruebas):**
   ```bash
   gcloud secrets versions disable 7 --secret=db-password --project=techo-chile
   ```

### Mejores Prácticas

1. ✅ **Usar versiones específicas** (`key: '7'`) en lugar de `latest` para control preciso
2. ✅ **Verificar formato** de contraseñas (sin saltos de línea, espacios extra)
3. ✅ **Probar en dev/staging** antes de rotación en producción
4. ✅ **Documentar cambios** con fecha y razón
5. ✅ **Mantener ventana de rollback** (no deshabilitar versión antigua inmediatamente)
6. ✅ **Auditar accesos** periódicamente con `gcloud secrets get-iam-policy`

### Comandos Útiles

```bash
# Listar todas las versiones del secret
gcloud secrets versions list db-password --project=techo-chile

# Ver valor de una versión específica (requiere permisos)
gcloud secrets versions access 7 --secret=db-password --project=techo-chile

# Ver política de IAM del secret
gcloud secrets get-iam-policy db-password --project=techo-chile

# Ver qué servicios usan el secret
gcloud run services list --project=techo-chile --format="table(metadata.name,spec.template.spec.containers[0].env)"
```

### Auditoría y Monitoreo

- **Último cambio**: 2025-12-01
- **Responsable**: Sistema de despliegue automatizado
- **Próxima revisión**: 2026-03-01
- **Versiones a limpiar**: 1-6 (después de verificar que v7 funciona correctamente en producción por 7+ días)

---

**Nota**: Este documento debe actualizarse cada vez que se realice una rotación de contraseñas o cambios en la configuración de secretos.
