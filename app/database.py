import os
import psycopg2
from config import DATABASE_URL
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from datetime import datetime, timedelta

# Create the database engine
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# Connection pool for better performance
CONNECTION_POOL = None

def get_db_connection():
    """Establishes a connection to the database."""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    """Initializes the database by creating all necessary tables with optimized indexes."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("DROP TABLE IF EXISTS meal_logs CASCADE;")
        cur.execute("DROP TABLE IF EXISTS insulin_doses CASCADE;")
        cur.execute("DROP TABLE IF EXISTS glucose_readings CASCADE;")
        cur.execute("DROP TABLE IF EXISTS activity_logs CASCADE;")
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
        # === OPTIMIZED INDEXES FOR ANALYTICS ===
        cur.execute("CREATE INDEX idx_glucose_user_time ON glucose_readings(user_id, timestamp DESC);")
        cur.execute("CREATE INDEX idx_glucose_timestamp ON glucose_readings(timestamp);")
        print("Created 'glucose_readings' table with optimized indexes.")

        cur.execute("""
            CREATE TABLE insulin_doses (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                dose_amount REAL NOT NULL,
                dose_type VARCHAR(50)
            );
        """)
        cur.execute("CREATE INDEX idx_insulin_user_time ON insulin_doses(user_id, timestamp DESC);")
        print("Created 'insulin_doses' table with index.")

        cur.execute("""
            CREATE TABLE meal_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                meal_description TEXT,
                carb_count REAL
            );
        """)
        cur.execute("CREATE INDEX idx_meal_user_time ON meal_logs(user_id, timestamp DESC);")
        print("Created 'meal_logs' table with index.")
        
        # === NEW: Activity logs table ===
        cur.execute("""
            CREATE TABLE activity_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                activity_type VARCHAR(100),
                duration_minutes INTEGER,
                intensity VARCHAR(50),
                notes TEXT
            );
        """)
        cur.execute("CREATE INDEX idx_activity_user_time ON activity_logs(user_id, timestamp DESC);")
        print("Created 'activity_logs' table with index.")

        conn.commit()
        print("Database initialized successfully with optimized indexes!")

    except Exception as e:
        print(f"An error occurred: {e}")
        if conn: conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()


# ==================================================================
# === OPTIMIZED ANALYTICS QUERIES ==================================
# ==================================================================

def get_glucose_readings_with_timestamps(user_id: int, days: int = 7, hours: int = None) -> list:
    """
    Get glucose readings with timestamps for analytics.
    Optimized query using the composite index.
    
    Args:
        user_id: User ID
        days: Number of days of data (default 7)
        hours: If specified, overrides days and gets last N hours
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if hours:
        interval = f"{hours} hours"
    else:
        interval = f"{days} days"
    
    # Optimized query with index hint ordering
    cur.execute(
        """
        SELECT timestamp, glucose_value 
        FROM glucose_readings
        WHERE user_id = %s AND timestamp >= NOW() - INTERVAL %s
        ORDER BY timestamp ASC;
        """,
        (user_id, interval)
    )
    readings = cur.fetchall()
    cur.close()
    conn.close()
    
    # Convert to serializable format
    return [
        {
            'timestamp': r['timestamp'].isoformat() if hasattr(r['timestamp'], 'isoformat') else str(r['timestamp']),
            'glucose_value': r['glucose_value']
        }
        for r in readings
    ]


def get_meal_logs_for_analytics(user_id: int, days: int = 7) -> list:
    """
    Get meal logs with timestamps for meal impact analysis.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute(
        """
        SELECT timestamp, meal_description, carb_count
        FROM meal_logs
        WHERE user_id = %s AND timestamp >= NOW() - INTERVAL '%s days'
        ORDER BY timestamp ASC;
        """,
        (user_id, days)
    )
    logs = cur.fetchall()
    cur.close()
    conn.close()
    
    return [
        {
            'timestamp': r['timestamp'].isoformat() if hasattr(r['timestamp'], 'isoformat') else str(r['timestamp']),
            'meal_description': r['meal_description'],
            'carb_count': r['carb_count']
        }
        for r in logs
    ]


def get_activity_logs(user_id: int, days: int = 7) -> list:
    """
    Get activity logs for analytics.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute(
            """
            SELECT timestamp, activity_type, duration_minutes, intensity, notes
            FROM activity_logs
            WHERE user_id = %s AND timestamp >= NOW() - INTERVAL '%s days'
            ORDER BY timestamp DESC;
            """,
            (user_id, days)
        )
        logs = cur.fetchall()
    except Exception:
        # Table might not exist in older schemas
        logs = []
    finally:
        cur.close()
        conn.close()
    
    return [
        {
            'timestamp': r['timestamp'].isoformat() if hasattr(r['timestamp'], 'isoformat') else str(r['timestamp']),
            'activity_type': r['activity_type'],
            'duration_minutes': r['duration_minutes'],
            'intensity': r.get('intensity'),
            'notes': r.get('notes')
        }
        for r in logs
    ]


def add_activity_log(user_id: int, activity_type: str, duration_minutes: int, intensity: str = None, notes: str = None):
    """Add an activity log entry."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            """
            INSERT INTO activity_logs (user_id, timestamp, activity_type, duration_minutes, intensity, notes)
            VALUES (%s, NOW(), %s, %s, %s, %s)
            """,
            (user_id, activity_type, duration_minutes, intensity, notes)
        )
        conn.commit()
        print(f"[Database] Activity logged for user {user_id}: {activity_type}")
    except Exception as e:
        print(f"[Database] Error logging activity: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def get_glucose_stats_by_hour(user_id: int, days: int = 7) -> dict:
    """
    Get aggregated glucose statistics by hour of day.
    Useful for pattern analysis and AGP.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute(
        """
        SELECT 
            EXTRACT(HOUR FROM timestamp) as hour,
            AVG(glucose_value) as avg_glucose,
            MIN(glucose_value) as min_glucose,
            MAX(glucose_value) as max_glucose,
            STDDEV(glucose_value) as std_glucose,
            COUNT(*) as reading_count,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY glucose_value) as median_glucose
        FROM glucose_readings
        WHERE user_id = %s AND timestamp >= NOW() - INTERVAL '%s days'
        GROUP BY EXTRACT(HOUR FROM timestamp)
        ORDER BY hour;
        """,
        (user_id, days)
    )
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    # Convert to dictionary keyed by hour
    return {int(r['hour']): {
        'avg': round(r['avg_glucose'], 1) if r['avg_glucose'] else None,
        'min': round(r['min_glucose'], 1) if r['min_glucose'] else None,
        'max': round(r['max_glucose'], 1) if r['max_glucose'] else None,
        'std': round(r['std_glucose'], 1) if r['std_glucose'] else None,
        'median': round(r['median_glucose'], 1) if r['median_glucose'] else None,
        'count': r['reading_count']
    } for r in results}


def get_glucose_stats_by_day_and_hour(user_id: int, days: int = 7) -> list:
    """
    Get aggregated glucose statistics by day of week and hour.
    Used for generating heatmap data.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute(
        """
        SELECT 
            EXTRACT(DOW FROM timestamp) as day_of_week,
            EXTRACT(HOUR FROM timestamp) as hour,
            AVG(glucose_value) as avg_glucose,
            COUNT(*) as reading_count
        FROM glucose_readings
        WHERE user_id = %s AND timestamp >= NOW() - INTERVAL '%s days'
        GROUP BY EXTRACT(DOW FROM timestamp), EXTRACT(HOUR FROM timestamp)
        ORDER BY day_of_week, hour;
        """,
        (user_id, days)
    )
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    return [
        {
            'day_of_week': int(r['day_of_week']),
            'hour': int(r['hour']),
            'avg_glucose': round(r['avg_glucose'], 1) if r['avg_glucose'] else None,
            'count': r['reading_count']
        }
        for r in results
    ]


def calculate_health_score(user_id: int) -> dict:
    """
    Calculates a daily 'Health Score' based on glucose data.
    First tries last 24 hours, then falls back to last 7 days, then all available data.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Try last 24 hours first
    cur.execute(
        """
        SELECT glucose_value FROM glucose_readings
        WHERE user_id = %s AND timestamp >= NOW() - INTERVAL '24 hours';
        """,
        (user_id,)
    )
    readings = cur.fetchall()
    
    # If not enough, try last 7 days
    if not readings or len(readings) < 5:
        cur.execute(
            """
            SELECT glucose_value FROM glucose_readings
            WHERE user_id = %s AND timestamp >= NOW() - INTERVAL '7 days';
            """,
            (user_id,)
        )
        readings = cur.fetchall()
    
    # If still not enough, get all readings
    if not readings or len(readings) < 5:
        cur.execute(
            """
            SELECT glucose_value FROM glucose_readings
            WHERE user_id = %s ORDER BY timestamp DESC LIMIT 100;
            """,
            (user_id,)
        )
        readings = cur.fetchall()
    
    cur.close()
    conn.close()
    
    if not readings or len(readings) < 3:  # Require at least 3 readings
        return { "score": 0, "time_in_range_percent": 0, "hypo_events_count": 0, "message": "Not enough glucose data to calculate score." }
        
    values = [r['glucose_value'] for r in readings]
    total_readings = len(values)
    
    # Scoring Logic - Based on percentages, not raw counts
    score = 100.0
    in_range_count = sum(1 for v in values if 70 <= v <= 180)
    time_in_range_percent = (in_range_count / total_readings) * 100
    
    # Main scoring: Time in range is the primary factor (max 50 points penalty)
    score -= (100 - time_in_range_percent) * 0.5
    
    # Hypo penalty based on percentage (max ~25 points penalty)
    hypo_events = sum(1 for v in values if v < 70)
    hypo_percent = (hypo_events / total_readings) * 100
    score -= hypo_percent * 0.5  # 0.5 points per percent of readings that are hypo
    
    # Severe hypo penalty (< 54 mg/dL) - additional penalty
    severe_hypo = sum(1 for v in values if v < 54)
    severe_hypo_percent = (severe_hypo / total_readings) * 100
    score -= severe_hypo_percent * 0.3  # Additional penalty for severe hypos
    
    # Very high penalty based on percentage
    very_high_events = sum(1 for v in values if v > 250)
    very_high_percent = (very_high_events / total_readings) * 100
    score -= very_high_percent * 0.2  # Smaller penalty for very highs
    
    final_score = max(0, min(100, int(round(score))))  # Clamp between 0-100
    
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