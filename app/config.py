import os

# Define the base directory of your project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to models
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'glucose_predictor.h5')
DATA_PATH = os.path.join(BASE_DIR, 'data', '559-ws-training.xml')

# --- THE FIX ---
# This line tells Python: "Look for a Secret named DATABASE_URL first."
# If it finds the Secret (which has port 6543), it uses it.
# If it doesn't find it (like on your laptop), it falls back to the hardcoded one.
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres.wcdjslqakemopfoiwwvh:swar%40123%23SWAR@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
)