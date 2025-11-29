import psycopg

conn = psycopg.connect(
    dbname="postgres",
    user="django_user",
    password="Internet3108",
    host="127.0.0.1",
    port="5432",
)

print("Conexión OK con psycopg3")
conn.close()
