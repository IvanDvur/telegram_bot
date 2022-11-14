import psycopg2
from config import host, user, db_name, password

try:
    conn = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

    cursor = conn.cursor()
    cursor.execute("SELECT appointment_time FROM therapist WHERE doctor_busy=FALSE LIMIT 1;")
    time = cursor.fetchone()
    print(time)
    print(time[0])

except Exception as e:
    print("Error", e)
finally:
    if conn:
        conn.close
        print("Connection was established")