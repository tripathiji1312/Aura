# file: test_prediction_server.py (Updated Version)

from flask import Flask, request, jsonify

# --- IMPORTANT: We now import your NEW master function from the SAME file ---
try:
    from prediction_service import generate_hybrid_prediction
except ImportError:
    print("\n--- ERROR ---")
    print("Could not find the function 'generate_hybrid_prediction' in 'prediction_service.py'.")
    print("Please make sure you have added the new master function to that file.")
    print("-------------\n")
    # A simple fallback so the app doesn't crash immediately
    def generate_hybrid_prediction(*args, **kwargs):
        return {"error": "The 'generate_hybrid_prediction' function was not found."}


# Initialize a new Flask application
app = Flask(__name__)


@app.route("/api/predict_hybrid", methods=['POST'])
def handle_hybrid_prediction():
    print("\n" + "="*50)
    print("Received a request at /api/predict_hybrid")
    
    # 1. Get the JSON data from the request
    data = request.get_json()
    
    # 2. Validate that the required 'history' key is present
    if not data or 'history' not in data:
        return jsonify({"error": "Invalid request. 'history' key is missing."}), 400
        
    history_data = data['history']
    print(f"-> Received glucose history: {history_data}")

    # 3. Get the optional 'future_events' data. Default to an empty dict if not provided.
    future_events = data.get('future_events', {})
    if future_events:
        print(f"-> Received future events: {future_events}")
    else:
        print("-> No future events provided, generating baseline prediction.")

    # 4. Call your new master AI function with both pieces of data
    prediction_response = generate_hybrid_prediction(
        recent_glucose_history=history_data,
        future_events=future_events
    )
    
    print("-> AI Service returned a complete response.")
    print("="*50 + "\n")

    # 5. Return the full, detailed JSON response from your service
    return jsonify(prediction_response)


# This block makes the server runnable directly from the command line
if __name__ == '__main__':
    print("Starting Enhanced Prediction Flask test server on http://127.0.0.1:5001")
    app.run(debug=True, port=5001)