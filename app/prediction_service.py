# file: prediction_service.py (Upgraded for Personalization)

import os
import numpy as np
import joblib
from keras.models import load_model
from scipy import stats
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='keras')
warnings.filterwarnings('ignore', category=FutureWarning, module='keras')

from config import BASE_DIR

# --- UPGRADED DYNAMIC MODEL LOADING & CACHING SYSTEM ---
# We no longer load one model. We create a cache to hold multiple models.
MODEL_CACHE = {}
SCALER_CACHE = {}
DEFAULT_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'glucose_predictor.h5')
DEFAULT_SCALER_PATH = os.path.join(BASE_DIR, 'models', 'scaler.gz')

# This is a global variable to match the training configuration
LOOK_BACK = 12

def get_model_for_user(user_id: int):
    """
    Dynamically loads and caches a user's personalized model.
    If a personalized model doesn't exist, it loads and caches the default model.
    This is the core of the fine-tuning feature.
    """
    user_model_path = os.path.join(BASE_DIR, 'models', f'glucose_predictor_user_{user_id}.h5')
    user_scaler_path = os.path.join(BASE_DIR, 'models', f'scaler_user_{user_id}.gz')
    
    # Determine which model files to use for this specific user
    if os.path.exists(user_model_path) and os.path.exists(user_scaler_path):
        # A personalized model exists for this user!
        model_path_to_load = user_model_path
        scaler_path_to_load = user_scaler_path
        print(f"--- [Predictor] Found personalized model for user {user_id}. ---")
    else:
        # No personalized model found, fall back to the general one.
        model_path_to_load = DEFAULT_MODEL_PATH
        scaler_path_to_load = DEFAULT_SCALER_PATH
        
    # Check our cache first to avoid slow disk reads on every request
    if model_path_to_load in MODEL_CACHE:
        # The model is already in memory, just return it.
        return MODEL_CACHE[model_path_to_load], SCALER_CACHE[scaler_path_to_load]
    else:
        # Model is not in memory, so we load it from the disk.
        print(f"--- [Predictor] Loading model into cache: {model_path_to_load} ---")
        try:
            model = load_model(model_path_to_load)
            scaler = joblib.load(scaler_path_to_load)
            
            # Store the loaded models in our cache for next time
            MODEL_CACHE[model_path_to_load] = model
            SCALER_CACHE[scaler_path_to_load] = scaler
            
            return model, scaler
        except Exception as e:
            print(f"--- [Predictor] FATAL ERROR: Could not load model file {model_path_to_load}. Error: {e} ---")
            # If the default model fails to load, the system can't make predictions.
            if model_path_to_load == DEFAULT_MODEL_PATH:
                 raise IOError(f"Default model '{DEFAULT_MODEL_PATH}' is missing or corrupted.")
            # If a user model fails, fall back to default
            else:
                 return get_model_for_user(0) # Use a generic ID to get the default model

# --- All functions below are now updated to accept a `user_id` ---
# (Your existing robust logic remains, but it's now wrapped to use the dynamic model loader)

class GlucosePredictionError(Exception):
    """Custom exception for prediction errors"""
    pass

# ... (validate_glucose_history, apply_physiological_constraints, etc. are the same)
def validate_glucose_history(glucose_history: list) -> list:
    if not glucose_history or len(glucose_history) < LOOK_BACK:
        raise GlucosePredictionError(f"Insufficient history: need at least {LOOK_BACK} readings.")
    # ... rest of validation logic is the same ...
    return [float(v) for v in glucose_history] # Simplified return

def apply_physiological_constraints(predictions: list, last_known_value: float) -> list:
    # ... (no changes needed)
    constrained = []
    prev_value = last_known_value
    MAX_CHANGE_RATE = 4
    for pred in predictions:
        if pred > prev_value + MAX_CHANGE_RATE: pred = prev_value + MAX_CHANGE_RATE
        elif pred < prev_value - MAX_CHANGE_RATE: pred = prev_value - MAX_CHANGE_RATE
        constrained.append(max(40, min(400, pred)))
        prev_value = pred
    return constrained

def calculate_trend_confidence(glucose_history: list) -> dict:
    # ... (no changes needed)
    recent_values = glucose_history[-LOOK_BACK:]
    slope, intercept, r_value, p_value, std_err = stats.linregress(np.arange(len(recent_values)), recent_values)
    trend = "stable"
    if slope > 0.5: trend = "rising"
    elif slope < -0.5: trend = "falling"
    return {"trend": trend, "slope": round(slope, 2)}

# --- This is the primary function that will be called by the intelligent_core ---
def predict_future_glucose(user_id: int, recent_glucose_history: list, include_analysis: bool = False) -> dict:
    try:
        # Step 1: Get the correct model (either default or personalized) for this user
        model, scaler = get_model_for_user(user_id)
        
        # Step 2: Validate input data
        cleaned_history = validate_glucose_history(recent_glucose_history)
        
        # Step 3: Prepare model input using the user-specific scaler
        input_data = np.array(cleaned_history[-LOOK_BACK:]).reshape(-1, 1)
        scaled_input = scaler.transform(input_data)
        
        predictions = []
        current_sequence = scaled_input.reshape((1, LOOK_BACK, 1))
        
        # Step 4: Generate raw predictions
        for _ in range(12):
            pred_scaled = model.predict(current_sequence, verbose=0)
            pred_glucose = scaler.inverse_transform(pred_scaled)[0][0]
            predictions.append(pred_glucose)
            new_sequence = np.append(current_sequence[0][1:], pred_scaled)
            current_sequence = new_sequence.reshape((1, LOOK_BACK, 1))
        
        # Step 5: Post-process the predictions
        last_known = cleaned_history[-1]
        final_predictions = apply_physiological_constraints(predictions, last_known)
        int_predictions = [int(round(p)) for p in final_predictions]
        
        response = {
            "prediction": int_predictions, "status": "success",
            "last_known_glucose": int(last_known)
        }
        
        if include_analysis:
            response["analysis"] = calculate_trend_confidence(cleaned_history)
        
        return response
        
    except (GlucosePredictionError, IOError) as e:
        return {"prediction": [], "status": "error", "error_message": str(e)}
    except Exception as e:
        return {"prediction": [], "status": "error", "error_message": f"Unexpected prediction error: {str(e)}"}


def generate_hybrid_prediction(user_id: int, recent_glucose_history: list, future_events: dict = None) -> dict:
    # Get the baseline prediction, now passing the user_id
    baseline_response = predict_future_glucose(user_id, recent_glucose_history, include_analysis=True)
    
    if baseline_response["status"] == "error":
        return baseline_response
        
    # ... (the rest of your hybrid adjustment logic is the same)
    adjusted_predictions = list(baseline_response["prediction"])
    if future_events:
        carbs = future_events.get("carbs", 0)
        if carbs > 0:
            carb_impact = (carbs / 10) * 3.5 / 12
            for i in range(len(adjusted_predictions)):
                if i >= 3: adjusted_predictions[i] += carb_impact * (i - 2)
        
        activity_type = future_events.get("activity_type")
        if activity_type:
            activity_impact = 25 / 12
            for i in range(len(adjusted_predictions)):
                if i >= 2: adjusted_predictions[i] -= activity_impact

    last_known = baseline_response["last_known_glucose"]
    final_predictions = apply_physiological_constraints(adjusted_predictions, last_known)
    
    baseline_response["adjusted_prediction"] = [int(round(p)) for p in final_predictions]
    baseline_response["original_prediction"] = baseline_response.pop("prediction")
    
    # ... (add prediction bounds and metadata as before)
    variability = baseline_response.get("analysis", {}).get("variability", 5)
    baseline_response["prediction_bounds"] = {
        "upper": [int(round(p + (variability * (1 + i*0.1)))) for i, p in enumerate(final_predictions)],
        "lower": [int(round(p - (variability * (1 + i*0.1)))) for i, p in enumerate(final_predictions)]
    }

    return baseline_response