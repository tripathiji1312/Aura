from natural_language_processor import EnhancedNLPProcessor
# --- We now import your NEW master prediction function ---
from prediction_service import generate_hybrid_prediction
from recommendation_service import get_insulin_recommendation
import database as db

# --- Initialize the AI components ---
# We create one instance of your NLP processor to use everywhere.
# This is efficient as it builds the lookup maps only once.
print("Initializing Enhanced NLP Processor...")
NLP_PROCESSOR = EnhancedNLPProcessor()
print("NLP Processor ready.")

def process_user_intent(user_id: int, user_text: str, glucose_history: list) -> dict:
    # Note: The function now accepts user_id as its first argument
    
    print(f"--- [AI Core] Processing intent for user {user_id}: '{user_text}' ---")
    
    # ... (NLP, Recommendation, and Advice logic is the same)
    parsed_entities = NLP_PROCESSOR.parse_user_text(user_text)
    carbs = parsed_entities.get("carbs", 0)
    activity_info = parsed_entities.get("activities_detected", [])
    activity_detected = len(activity_info) > 0
    
    current_glucose = glucose_history[-1] if glucose_history else 120
    dose_recommendation = get_insulin_recommendation(
        glucose=current_glucose,
        carbs=carbs,
        exercise_recent=activity_detected
    )
    
    # 3. PREDICT (This is the line that changes)
    future_events = {
        "carbs": carbs,
        "activity_type": activity_info[0]['activity'] if activity_info else None,
        "activity_duration": activity_info[0]['duration_minutes'] if activity_info else 0
    }
    
    # <<< THE CHANGE IS HERE: We now pass the user_id >>>
    hybrid_prediction = generate_hybrid_prediction(
        user_id=user_id, # Pass the user_id to the prediction service
        recent_glucose_history=glucose_history,
        future_events=future_events
    )
    
    contextual_advice = NLP_PROCESSOR.get_insulin_adjustment_suggestion(parsed_entities)
    
    # ... (Assemble the response as before)
    response = {
        "parsed_info": parsed_entities,
        "dose_recommendation": dose_recommendation,
        "glucose_prediction": hybrid_prediction,
        "contextual_advice": contextual_advice
    }
    
    print(f"--- [AI Core] Intent processed successfully. ---")
    return response