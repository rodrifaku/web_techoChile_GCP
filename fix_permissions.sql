-- Script para otorgar permisos a postgres sobre tablas de django_user
-- y resetear contraseña de django_user

-- Conectar a la base de datos django_db
\c django_db

-- Otorgar todos los privilegios a postgres sobre el esquema público
GRANT ALL PRIVILEGES ON DATABASE django_db TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO postgres;

-- Resetear la contraseña de django_user
ALTER USER django_user WITH PASSWORD '3cXQregTwFpK9aIno5JDV8YB';

-- Otorgar todos los privilegios a django_user también (asegurar que tenga acceso)
GRANT ALL PRIVILEGES ON DATABASE django_db TO django_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO django_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO django_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO django_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO django_user;

-- Establecer permisos por defecto para futuros objetos
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO postgres, django_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO postgres, django_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO postgres, django_user;

-- Confirmar cambios
\echo 'Permisos otorgados correctamente'
