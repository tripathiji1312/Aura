import os
import psycopg2
from config import DATABASE_URL
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine # Added import for create_engine

# Create the database engine
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

def get_db_connection():
    """Establishes a connection to the database."""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    """Initializes the database by creating all necessary tables."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("DROP TABLE IF EXISTS meal_logs CASCADE;")
        cur.execute("DROP TABLE IF EXISTS insulin_doses CASCADE;")
        cur.execute("DROP TABLE IF EXISTS glucose_readings CASCADE;")
        cur.execute("DROP TABLE IF EXISTS users CASCADE;")
        print("Dropped existing tables.")

        cur.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL, 
                password_hash VARCHAR(256) NOT NULL,
                name VARCHAR(100) NOT NULL,
                age INTEGER,
                gender VARCHAR(50),
                phone_number VARCHAR(20),
                weight_kg REAL,
                height_cm REAL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("Created UPGRADED 'users' table.")

        cur.execute("""
            CREATE TABLE glucose_readings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                glucose_value REAL NOT NULL
            );
        """)
        print("Created 'glucose_readings' table.")

        cur.execute("""
            CREATE TABLE insulin_doses (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                dose_amount REAL NOT NULL,
                dose_type VARCHAR(50)
            );
        """)
        print("Created 'insulin_doses' table.")

        cur.execute("""
            CREATE TABLE meal_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                meal_description TEXT,
                carb_count REAL
            );
        """)
        print("Created 'meal_logs' table.")

        conn.commit()
        print("Database initialized successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
        if conn: conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()
def calculate_health_score(user_id: int) -> dict:
    """
    Calculates a daily 'Health Score' based on the last 24 hours of glucose data.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute(
        """
        SELECT glucose_value FROM glucose_readings
        WHERE user_id = %s AND timestamp >= NOW() - INTERVAL '24 hours';
        """,
        (user_id,)
    )
    readings = cur.fetchall()
    cur.close()
    conn.close()
    
    if not readings or len(readings) < 10: # Require at least 10 readings
        return { "score": None, "time_in_range_percent": None, "message": "Not enough data from the last 24 hours to calculate a score." }
        
    values = [r['glucose_value'] for r in readings]
    total_readings = len(values)
    
    # Scoring Logic
    score = 100.0
    in_range_count = sum(1 for v in values if 70 <= v <= 180)
    time_in_range_percent = (in_range_count / total_readings) * 100
    
    score -= (100 - time_in_range_percent) * 0.5 # Penalty for being out of range
    
    hypo_events = sum(1 for v in values if v < 70)
    score -= hypo_events * 5 # Heavy penalty for lows
    
    very_high_events = sum(1 for v in values if v > 250)
    score -= very_high_events * 2 # Smaller penalty for very highs
    
    final_score = max(0, int(round(score)))
    
    return {
        "score": final_score,
        "time_in_range_percent": round(time_in_range_percent, 1),
        "hypo_events_count": hypo_events,
    }
def find_user_by_username(username: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s;", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def get_recent_glucose_readings(user_id: int, limit: int = 100):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT glucose_value FROM glucose_readings WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s;", (user_id, limit))
    readings = cur.fetchall()
    cur.close()
    conn.close()
    if not readings: return []
    return [r['glucose_value'] for r in reversed(readings)]

def get_dashboard_data_for_user(user_id: int):
    """
    Fetches all necessary data for the user's dashboard,
    now INCLUDING the Health Score.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # --- Part 1: Fetch core data (your existing code is perfect) ---
    
    # Fetch user profile info
    cur.execute("SELECT name, age, weight_kg, height_cm FROM users WHERE id = %s;", (user_id,))
    user_profile = cur.fetchone()

    # Fetch glucose readings for the chart
    cur.execute(
        """
        SELECT timestamp, glucose_value FROM glucose_readings 
        WHERE user_id = %s AND timestamp > NOW() - INTERVAL '24 hours' 
        ORDER BY timestamp ASC;
        """, 
        (user_id,)
    )
    glucose_readings = cur.fetchall()
    
    # Fetch recent meals for the log
    cur.execute(
        """
        SELECT timestamp, meal_description, carb_count FROM meal_logs 
        WHERE user_id = %s AND timestamp > NOW() - INTERVAL '24 hours' 
        ORDER BY timestamp DESC LIMIT 5;
        """, 
        (user_id,)
    )
    meal_logs = cur.fetchall()
    
    # --- Part 2: Clean up the database connection ---
    cur.close()
    conn.close()
    
    # --- Part 3: (THE NEW PART) Call the health score function ---
    # We do this after closing the main connection to keep things clean.
    # The calculate_health_score function opens and closes its own connection.
    health_score_data = calculate_health_score(user_id)
    
    # --- Part 4: Assemble the complete response ---
    # We now add the 'health_score' key to the dictionary we return.
    return {
        "user_profile": user_profile,
        "glucose_readings": glucose_readings,
        "recent_meals": meal_logs,
        "health_score": health_score_data # <-- THIS IS THE NEWLY ADDED PIECE
    }

def add_log_entry(user_id: int, log_type: str, description: str, value: float):
    """Adds a new log entry to the appropriate table."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    if log_type == 'meal':
        sql = "INSERT INTO meal_logs (user_id, timestamp, meal_description, carb_count) VALUES (%s, NOW(), %s, %s)"
        cur.execute(sql, (user_id, description, value))
    elif log_type == 'insulin':
        sql = "INSERT INTO insulin_doses (user_id, timestamp, dose_amount, dose_type) VALUES (%s, NOW(), %s, %s)"
        # 'description' would be 'bolus' or 'basal' in this case
        cur.execute(sql, (user_id, value, description))
    # Add other log types here (e.g., 'activity')
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"--- [Database] Saved '{log_type}' log for user {user_id}. ---")

if __name__ == '__main__':
    print("Initializing database...")
    init_db()