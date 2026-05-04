import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# Default to local postgres if not specified
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/network_anomaly")

def get_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def init_db():
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS anomaly_logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    prediction VARCHAR(20),
                    xgb_score FLOAT,
                    iso_score FLOAT,
                    ae_score FLOAT,
                    final_score FLOAT,
                    details JSONB
                );
            """)
            conn.commit()
        conn.close()
        print("Database initialized successfully ✅")

def log_anomaly(prediction, xgb_score, iso_score, ae_score, final_score, details):
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO anomaly_logs (prediction, xgb_score, iso_score, ae_score, final_score, details)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (prediction, xgb_score, iso_score, ae_score, final_score, details))
            conn.commit()
        conn.close()

def get_recent_logs(limit=100):
    conn = get_connection()
    if conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM anomaly_logs ORDER BY timestamp DESC LIMIT %s", (limit,))
            rows = cur.fetchall()
        conn.close()
        return rows
    return []

if __name__ == "__main__":
    init_db()
