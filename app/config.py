import os

# Define the base directory of your project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to models (Using relative paths)
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'glucose_predictor.h5')
DATA_PATH = os.path.join(BASE_DIR, 'data', '559-ws-training.xml')

# Database: PostgreSQL (Supabase)
# WARNING: Contains sensitive credentials. Do not push to public repositories without using environment variables in production.
DATABASE_URL = "postgresql://postgres:swar%40123%23SWAR@db.wcdjslqakemopfoiwwvh.supabase.co:5432/postgres"