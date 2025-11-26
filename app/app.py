import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import database as db
import simulator
from intelligent_core import process_user_intent
import threading
import model_trainer
from flask import send_file
import report_generator
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend for matplotlib

# Import new services
from analytics_service import get_full_analytics, ClinicalMetrics, AGPCalculator, PatternAnalyzer, AdvancedGlucoseAnalytics
from cache_service import cache, on_new_glucose_reading, on_new_meal_log, on_model_calibration
from websocket_service import (
    socketio, broadcast_glucose_update, broadcast_prediction_update,
    broadcast_health_score_update, broadcast_dashboard_refresh,
    broadcast_calibration_status, get_connection_stats, check_and_send_proactive_alerts
)

app = Flask(__name__, static_url_path='', static_folder='static')

# --- UPGRADED CORS CONFIGURATION ---
# This explicitly allows your frontend's origin to access the backend API.
# NOTE: Update the origin port if your frontend runs on a different one (e.g., 3000 for React)
CORS(app, origins="*") # Allow all origins for production/Hugging Face

# Initialize WebSocket
socketio.init_app(app)
print("[App] WebSocket initialized with Flask-SocketIO")
# ------------------------------------

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/health')
def health_check():
    return "Project Aura Backend is running!"

@app.route("/register", methods=['POST'], strict_slashes=False)
def register():
    data = request.get_json()
    username, password, name = data.get('username'), data.get('password'), data.get('name')
    age, gender, phone, weight, height = data.get('age'), data.get('gender'), data.get('phone_number'), data.get('weight_kg'), data.get('height_cm')

    if not all([username, password, name]):
        return jsonify({"error": "Username, password, and name are required"}), 400

    if db.find_user_by_username(username):
        return jsonify({"error": "Username already taken"}), 409

    hashed_password = generate_password_hash(password)
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, password_hash, name, age, gender, phone_number, weight_kg, height_cm) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (username, hashed_password, name, age, gender, phone, weight, height)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "User registered successfully!"}), 201

@app.route("/login", methods=['POST'], strict_slashes=False)
def login():
    data = request.get_json()
    username, password = data.get('username'), data.get('password')
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    user = db.find_user_by_username(username)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({"message": "Login successful", "token": "mock_jwt_for_hackathon", "user_id": user['id']})

# In app.py

# ... (keep all other code the same) ...
# ==================================================================
# === THE PRIMARY AI ENDPOINT (FINAL DEBUG VERSION) ================
# ==================================================================
@app.route("/api/chat", methods=['POST'])
def handle_chat_intent():
    print("\n" + "="*50)
    print("--- Received request at /api/chat ---")
    data = request.get_json()
    
    user_message = data.get('message')
    user_id = data.get('user_id')

    if not user_message or not user_id:
        print("--- [ERROR] Request is missing 'message' or 'user_id'. ---")
        return jsonify({"error": "A 'message' and 'user_id' are required"}), 400
        
    print(f"--- [INPUT] User ID: {user_id}, Message: '{user_message}'")
    
    # --- Step 1: Get Glucose History ---
    glucose_history = db.get_recent_glucose_readings(user_id, limit=12)
    if not glucose_history or len(glucose_history) < 12:
        print(f"--- [DATA] Found only {len(glucose_history)} readings. Using fallback mock data for AI. ---")
        glucose_history = [120, 122, 125, 126, 128, 129, 130, 131, 130, 128, 126, 124]
    else:
        print(f"--- [DATA] Found {len(glucose_history)} recent glucose readings. ---")

    # --- Step 2: Call the AI Core ---
    print("--- [AI] Calling 'process_user_intent'... ---")
    ai_response = process_user_intent(
        user_id=user_id,
        user_text=user_message,
        glucose_history=glucose_history
    )
    
    # --- !! CRITICAL DEBUGGING STEP !! ---
    # We will now print the entire raw response from the AI to see exactly what it contains.
    import json
    print("--- [AI] Raw response from AI Core:")
    print(json.dumps(ai_response, indent=2))
    # ----------------------------------------

    # --- Step 3: Save Detected Meals to Database ---
    print("--- [DATABASE] Checking AI response for meals to save... ---")
    try:
        # More robust check: ensure keys exist before accessing them
        if "parsed_info" in ai_response and "foods_detected" in ai_response["parsed_info"]:
            foods_to_log = ai_response["parsed_info"]["foods_detected"]
            
            if foods_to_log: # Check if the list is not empty
                print(f"--- [DATABASE] Found {len(foods_to_log)} food item(s). Proceeding to save. ---")
                for food_item in foods_to_log:
                    description = f"{food_item.get('quantity', 1)}x {food_item.get('food', 'Unknown Food')}"
                    carb_value = food_item.get('carbs', 0)
                    
                    print(f"--- [DATABASE] Saving: User='{user_id}', Desc='{description}', Carbs='{carb_value}'")
                    db.add_log_entry(
                        user_id=int(user_id),
                        log_type='meal',
                        description=description,
                        value=carb_value
                    )
                print("--- [DATABASE] All detected meals have been saved. ---")
            else:
                print("--- [DATABASE] 'foods_detected' list was empty. Nothing to save. ---")
        else:
            print("--- [DATABASE] 'parsed_info' or 'foods_detected' key not found in AI response. Nothing to save. ---")
            
    except Exception as e:
        print(f"--- [DATABASE] CRITICAL ERROR during save process. The AI response was processed, but saving failed. ---")
        print(f"--- [DATABASE] Error details: {e} ---")
    
    print("--- AI Core processed intent successfully. Returning response to frontend. ---")
    print("="*50 + "\n")
    return jsonify(ai_response)
# ==================================================================
# === NEW: AI CALIBRATION ENDPOINT =================================
# ==================================================================
@app.route('/api/ai/calibrate', methods=['POST'])
def calibrate_ai_for_user():
    """
    Triggers the AI fine-tuning process for a specific user in the background.
    """
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"error": "A 'user_id' is required"}), 400
        
    print(f"--- [API] Received calibration request for user_id: {user_id} ---")
    
    # Run the slow training process in a separate thread
    # This allows us to send an immediate "started" response back to the frontend
    # without making the user wait for the training to finish.
    training_thread = threading.Thread(
        target=model_trainer.fine_tune_model_for_user,
        args=(int(user_id),) # Ensure user_id is an integer
    )
    training_thread.start() # Start the background task
    
    # Immediately return a 202 Accepted response to the frontend
    return jsonify({
        "status": "Calibration Initiated",
        "message": f"AI model personalization has started for user {user_id}. " \
                   "This process runs in the background and may take several minutes. " \
                   "Predictions will automatically use the new model once complete."
    }), 202
@app.route("/api/dashboard", methods=['GET'])
def get_dashboard():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "A 'user_id' query parameter is required"}), 400

    dashboard_data = db.get_dashboard_data_for_user(user_id)
    return jsonify(dashboard_data)
# ==================================================================
# === NEW: PDF REPORT DOWNLOAD ENDPOINT ============================
# ==================================================================
@app.route('/api/user/report', methods=['POST'])
def download_user_report():
    """
    Generates a PDF report for a user and sends it as a file download.
    """
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"error": "A 'user_id' in the request body is required"}), 400
        
    print(f"--- [API] Received report generation request for user_id: {user_id} ---")
    
    try:
        # Call the report generator, which returns the path and a clean filename
        pdf_path, pdf_filename = report_generator.create_user_report(int(user_id))
        
        # Send the generated file back to the browser for download
        return send_file(
            pdf_path, 
            as_attachment=True, 
            download_name=pdf_filename # This is the name the user will see
        )
        
    except Exception as e:
        print(f"--- [API] ERROR: Failed to generate report. Error: {e} ---")
        return jsonify({"error": f"An error occurred while generating the report: {e}"}), 500
@app.route('/api/dev/simulate-data', methods=['POST'])
def simulate_data_endpoint():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"error": "A 'user_id' is required"}), 400
    try:
        simulator.generate_and_insert_data(user_id=user_id, days_of_data=3)
        # Invalidate cache and broadcast update
        cache.invalidate_all_user_cache(int(user_id))
        broadcast_dashboard_refresh(int(user_id), "demo_data_added")
        return jsonify({'message': f'Successfully generated 3 days of data for user {user_id}.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================================================================
# === ADVANCED ANALYTICS ENDPOINTS =================================
# ==================================================================

@app.route('/api/analytics/full', methods=['GET'])
def get_advanced_analytics():
    """
    Get comprehensive analytics including AGP, GMI, CV, and pattern analysis.
    
    Query params:
        - user_id: Required
        - days: Number of days to analyze (default: 7, max: 30)
    """
    user_id = request.args.get('user_id')
    days = min(int(request.args.get('days', 7)), 30)
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    try:
        # Get readings and meal logs from database
        readings = db.get_glucose_readings_with_timestamps(int(user_id), days=days)
        meal_logs = db.get_meal_logs_for_analytics(int(user_id), days=days)
        
        if not readings:
            return jsonify({"error": "No glucose data available for analysis"}), 404
        
        # Generate full analytics
        analytics = get_full_analytics(int(user_id), readings, meal_logs, days=days)
        
        return jsonify(analytics)
    except Exception as e:
        print(f"[Analytics] Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/analytics/agp', methods=['GET'])
def get_agp_data():
    """
    Get Ambulatory Glucose Profile (AGP) data.
    Returns percentile curves for 24-hour glucose patterns.
    """
    user_id = request.args.get('user_id')
    days = min(int(request.args.get('days', 14)), 30)
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    try:
        readings = db.get_glucose_readings_with_timestamps(int(user_id), days=days)
        
        if not readings or len(readings) < 20:
            return jsonify({"error": "Insufficient data for AGP (need at least 20 readings)"}), 404
        
        agp_data = AGPCalculator.calculate_agp(readings, days)
        return jsonify(agp_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/analytics/clinical-metrics', methods=['GET'])
def get_clinical_metrics():
    """
    Get clinical-grade metrics: GMI, CV, Time in Range breakdown, Risk indices.
    """
    user_id = request.args.get('user_id')
    days = min(int(request.args.get('days', 7)), 30)
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    try:
        readings = db.get_glucose_readings_with_timestamps(int(user_id), days=days)
        
        if not readings:
            return jsonify({"error": "No glucose data available"}), 404
        
        glucose_values = [r.get('glucose_value') for r in readings if r.get('glucose_value')]
        
        import numpy as np
        metrics = {
            "mean_glucose": round(np.mean(glucose_values), 1),
            "std_glucose": round(np.std(glucose_values), 1),
            "gmi": ClinicalMetrics.calculate_gmi(np.mean(glucose_values)),
            "cv": ClinicalMetrics.calculate_cv(glucose_values),
            "time_in_range": ClinicalMetrics.calculate_time_in_range(glucose_values),
            "risk_indices": ClinicalMetrics.calculate_glucose_risk_index(glucose_values),
            "total_readings": len(glucose_values),
            "days_analyzed": days
        }
        
        return jsonify(metrics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/analytics/patterns', methods=['GET'])
def get_pattern_analysis():
    """
    Get pattern analysis: time-of-day breakdown, dawn phenomenon, heatmap data.
    """
    user_id = request.args.get('user_id')
    days = min(int(request.args.get('days', 7)), 30)
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    try:
        readings = db.get_glucose_readings_with_timestamps(int(user_id), days=days)
        
        if not readings:
            return jsonify({"error": "No glucose data available"}), 404
        
        patterns = {
            "by_time_period": PatternAnalyzer.analyze_by_time_period(readings),
            "dawn_phenomenon": PatternAnalyzer.detect_dawn_phenomenon(readings),
            "heatmap": PatternAnalyzer.generate_pattern_heatmap(readings)
        }
        
        return jsonify(patterns)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/analytics/advanced', methods=['GET'])
def get_advanced_analytics_combined():
    """
    Combined endpoint for all advanced analytics data.
    Returns AGP, GMI, CV, time-of-day patterns, and distribution in one call.
    Optimized for the analytics dashboard.
    """
    user_id = request.args.get('user_id')
    days = min(int(request.args.get('days', 7)), 30)
    
    if not user_id:
        return jsonify({"success": False, "error": "user_id is required"}), 400
    
    try:
        # Check cache first
        cache_key = f"advanced_analytics:{user_id}:{days}"
        cached = cache.get(cache_key)
        if cached:
            return jsonify(cached)
        
        # Get readings with timestamps
        readings = db.get_glucose_readings_with_timestamps(int(user_id), days=days)
        
        if not readings or len(readings) < 3:
            return jsonify({
                "success": False, 
                "error": "Not enough data for advanced analytics",
                "readings_count": len(readings) if readings else 0
            }), 404
        
        # Extract glucose values
        glucose_values = [r['glucose_value'] for r in readings]
        
        # Calculate all metrics
        analytics_engine = AdvancedGlucoseAnalytics()
        
        # AGP
        agp = analytics_engine.calculate_agp(readings)
        
        # GMI (Glucose Management Indicator)
        avg_glucose = sum(glucose_values) / len(glucose_values)
        gmi = analytics_engine.calculate_gmi(avg_glucose)
        
        # Coefficient of Variation
        cv = analytics_engine.calculate_coefficient_of_variation(glucose_values)
        
        # Time of day patterns (for heatmap)
        time_patterns = analytics_engine.get_time_of_day_patterns(readings)
        
        # Distribution
        low = len([v for v in glucose_values if v < 70])
        normal = len([v for v in glucose_values if 70 <= v <= 180])
        high = len([v for v in glucose_values if v > 180])
        total = len(glucose_values)
        
        # Time in range
        tir = (normal / total) * 100 if total > 0 else 0
        
        # Hypo events
        hypo_events = low
        
        result = {
            "success": True,
            "user_id": user_id,
            "days_analyzed": days,
            "readings_count": total,
            "average_glucose": round(avg_glucose, 1),
            "gmi": round(gmi, 2),
            "cv": round(cv, 2),
            "time_in_range": round(tir, 1),
            "hypo_events": hypo_events,
            "agp": agp,
            "time_of_day_patterns": time_patterns,
            "distribution": {
                "low": round((low / total) * 100, 1) if total > 0 else 0,
                "normal": round((normal / total) * 100, 1) if total > 0 else 0,
                "high": round((high / total) * 100, 1) if total > 0 else 0
            }
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, result, ttl=300)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"[Advanced Analytics] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/analytics/meal-impact', methods=['GET'])
def get_meal_impact_analysis():
    """
    Analyze how meals affect glucose levels.
    """
    user_id = request.args.get('user_id')
    days = min(int(request.args.get('days', 7)), 30)
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    try:
        readings = db.get_glucose_readings_with_timestamps(int(user_id), days=days)
        meal_logs = db.get_meal_logs_for_analytics(int(user_id), days=days)
        
        if not readings or not meal_logs:
            return jsonify({"error": "Insufficient data for meal impact analysis"}), 404
        
        impact = PatternAnalyzer.analyze_meal_impact(readings, meal_logs)
        return jsonify(impact)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================================================================
# === CACHE & WEBSOCKET MANAGEMENT ENDPOINTS =======================
# ==================================================================

@app.route('/api/cache/health', methods=['GET'])
def cache_health_check():
    """Check cache service health status."""
    return jsonify(cache.health_check())


@app.route('/api/cache/invalidate', methods=['POST'])
def invalidate_user_cache():
    """Manually invalidate all cache for a user."""
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    result = cache.invalidate_all_user_cache(int(user_id))
    return jsonify({"message": "Cache invalidated", "details": result})


@app.route('/api/websocket/stats', methods=['GET'])
def websocket_stats():
    """Get WebSocket connection statistics."""
    return jsonify(get_connection_stats())


# ==================================================================
# === LAZY LOADING ENDPOINTS =======================================
# ==================================================================

@app.route('/api/dashboard/glucose-chart', methods=['GET'])
def get_glucose_chart_data():
    """
    Lazy-loaded endpoint for glucose chart data only.
    """
    user_id = request.args.get('user_id')
    hours = int(request.args.get('hours', 24))
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    try:
        readings = db.get_glucose_readings_with_timestamps(int(user_id), hours=hours)
        return jsonify({
            "readings": readings,
            "count": len(readings) if readings else 0
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/dashboard/health-score', methods=['GET'])
def get_health_score_only():
    """
    Lazy-loaded endpoint for health score only.
    """
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    try:
        health_score = db.calculate_health_score(int(user_id))
        return jsonify(health_score)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    """
    Lazy-loaded endpoint for dashboard metrics (TIR, avg glucose, etc.)
    """
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    try:
        readings = db.get_recent_glucose_readings(int(user_id), limit=100)
        
        if not readings:
            return jsonify({"error": "No readings available"}), 404
        
        import numpy as np
        metrics = {
            "avg_glucose": round(np.mean(readings), 1),
            "time_in_range": ClinicalMetrics.calculate_time_in_range(readings)["in_range"],
            "cv": ClinicalMetrics.calculate_cv(readings),
            "reading_count": len(readings)
        }
        return jsonify(metrics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(app, host='0.0.0.0', port=7860, debug=False, allow_unsafe_werkzeug=True)