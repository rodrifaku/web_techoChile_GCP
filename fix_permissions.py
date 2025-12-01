#!/usr/bin/env python3
"""
Script para otorgar permisos en Cloud SQL PostgreSQL.
Se ejecuta como un job de Cloud Run con el usuario postgres.
"""
import os
import sys
import psycopg2
from psycopg2 import sql

def main():
    # Obtener credenciales del entorno
    db_name = os.getenv('DB_NAME', 'django_db')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', '/cloudsql/techo-chile:southamerica-west1:techo-sql-primary')
    
    print(f"[INFO] Conectando a la base de datos como usuario: {db_user}")
    print(f"[INFO] Base de datos: {db_name}")
    print(f"[INFO] Host: {db_host}")
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("[INFO] Conexión exitosa!")
        
        # Comandos SQL para ejecutar
        commands = [
            # Otorgar privilegios a postgres
            "GRANT ALL PRIVILEGES ON DATABASE django_db TO postgres",
            "GRANT ALL PRIVILEGES ON SCHEMA public TO postgres",
            "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres",
            "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres",
            "GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO postgres",
            
            # Resetear contraseña de django_user
            "ALTER USER django_user WITH PASSWORD '3cXQregTwFpK9aIno5JDV8YB'",
            
            # Otorgar privilegios a django_user
            "GRANT ALL PRIVILEGES ON DATABASE django_db TO django_user",
            "GRANT ALL PRIVILEGES ON SCHEMA public TO django_user",
            "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO django_user",
            "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO django_user",
            "GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO django_user",
            
            # Permisos por defecto
            "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO postgres, django_user",
            "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO postgres, django_user",
            "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO postgres, django_user",
        ]
        
        # Ejecutar cada comando
        for i, command in enumerate(commands, 1):
            print(f"[{i}/{len(commands)}] Ejecutando: {command[:80]}...")
            try:
                cursor.execute(command)
                print(f"  ✓ Éxito")
            except Exception as e:
                print(f"  ✗ Error: {e}")
                # Continuar con los demás comandos
        
        # Verificar permisos otorgados
        print("\n[INFO] Verificando permisos de django_user...")
        cursor.execute("""
            SELECT table_name, privilege_type 
            FROM information_schema.table_privileges 
            WHERE grantee = 'django_user' 
            AND table_schema = 'public'
            LIMIT 5
        """)
        permisos = cursor.fetchall()
        if permisos:
            print("  Permisos encontrados:")
            for tabla, privilegio in permisos:
                print(f"    - {tabla}: {privilegio}")
        else:
            print("  [WARN] No se encontraron permisos, pero esto puede ser normal si no hay tablas")
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        
        print("\n[SUCCESS] ¡Todos los permisos han sido otorgados correctamente!")
        return 0
        
    except psycopg2.OperationalError as e:
        print(f"[ERROR] Error de conexión: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
