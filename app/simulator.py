import random
import psycopg2
from datetime import datetime, timedelta, timezone
from database import get_db_connection

def clear_user_data(user_id):
    """Deletes all non-user data for a specific user to ensure a clean slate."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM meal_logs WHERE user_id = %s;", (user_id,))
        cur.execute("DELETE FROM insulin_doses WHERE user_id = %s;", (user_id,))
        cur.execute("DELETE FROM glucose_readings WHERE user_id = %s;", (user_id,))
        conn.commit()
        print(f"Cleared existing data for user_id: {user_id}")
    except Exception as e:
        print(f"An error occurred while clearing data: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

# In simulator.py

# ... (keep the clear_user_data function and imports the same) ...

def generate_and_insert_data(user_id, days_of_data=3):
    """
    Generates and inserts more realistic time-series data.
    """
    clear_user_data(user_id)
    conn = get_db_connection()
    cur = conn.cursor()

    now = datetime.now(timezone.utc)
    start_time = now - timedelta(days=days_of_data)
    current_time = start_time
    
    # Start with a more realistic, stable glucose
    current_glucose = random.uniform(90, 130)
    # This will track the effect of insulin over time
    active_insulin_effect = 0 
    
    glucose_readings_to_insert = []
    print(f"Generating data from {start_time} to {now}...")

    while current_time < now:
        # --- NEW REALISTIC LOGIC ---

        # 1. Natural glucose drift (liver production)
        current_glucose += random.uniform(-0.5, 1.0) # Slight upward pressure

        # 2. Insulin Effect: Insulin given previously is still working
        if active_insulin_effect > 0:
            glucose_drop_from_insulin = random.uniform(2, 5)
            current_glucose -= glucose_drop_from_insulin
            active_insulin_effect -= glucose_drop_from_insulin

        # 3. Handle Meals
        is_meal_time = (7 <= current_time.hour <= 9) or \
                       (12 <= current_time.hour <= 14) or \
                       (18 <= current_time.hour <= 20)

        if is_meal_time and random.random() < 0.15: # Less frequent but adds up
            meal_carbs = random.randint(30, 80)
            meal_description = f"Simulated Meal ({meal_carbs}g)"
            cur.execute(
                "INSERT INTO meal_logs (user_id, timestamp, meal_description, carb_count) VALUES (%s, %s, %s, %s)",
                (user_id, current_time, meal_description, meal_carbs)
            )
            
            insulin_dose = round(meal_carbs / 12, 1) # Using a 1:12 ratio
            cur.execute(
                "INSERT INTO insulin_doses (user_id, timestamp, dose_amount, dose_type) VALUES (%s, %s, %s, %s)",
                (user_id, current_time, insulin_dose, 'bolus')
            )

            # Carbs cause a rise, but insulin will cause a drop.
            # We model the total effect of insulin over the next few hours.
            # 1 unit of insulin will lower BG by ~40 points total.
            active_insulin_effect += insulin_dose * 40
            # Carbs have an immediate, but smaller, impact.
            current_glucose += meal_carbs * 0.75

        # 4. Apply physiological constraints
        if current_glucose < 50:
            current_glucose += random.uniform(5, 15) # Body tries to correct a low
        if current_glucose > 350:
            current_glucose = 350 # Cap at a high but not absurd value

        glucose_readings_to_insert.append((user_id, current_time, round(current_glucose, 2)))
        current_time += timedelta(minutes=5)
    
    # --- The insertion logic remains the same ---
    print(f"Inserting {len(glucose_readings_to_insert)} glucose readings...")
    try:
        for reading in glucose_readings_to_insert:
            cur.execute(
                "INSERT INTO glucose_readings (user_id, timestamp, glucose_value) VALUES (%s, %s, %s)",
                reading
            )
        conn.commit()
        print(f"Successfully inserted {len(glucose_readings_to_insert)} readings.")
    except Exception as e:
        print(f"An error occurred during insert: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

# ... (keep the if __name__ == '__main__' block) ...


if __name__ == '__main__':
    print("Running data simulator standalone...")
    generate_and_insert_data(user_id=1, days_of_data=3)
    print("Simulator finished.")