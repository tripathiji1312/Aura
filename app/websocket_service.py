# file: websocket_service.py
# Real-time WebSocket service for Aura using Flask-SocketIO

from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
from typing import Dict, Any, Optional
import json

# Initialize SocketIO (will be attached to Flask app in app.py)
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')

# Track connected users and their rooms
connected_users: Dict[str, set] = {}  # user_id -> set of session_ids


class WebSocketEvents:
    """WebSocket event names"""
    CONNECT = 'connect'
    DISCONNECT = 'disconnect'
    JOIN_USER_ROOM = 'join_user_room'
    LEAVE_USER_ROOM = 'leave_user_room'
    
    # Server -> Client events
    GLUCOSE_UPDATE = 'glucose_update'
    PREDICTION_UPDATE = 'prediction_update'
    HEALTH_SCORE_UPDATE = 'health_score_update'
    ALERT = 'alert'
    DASHBOARD_REFRESH = 'dashboard_refresh'
    CALIBRATION_STATUS = 'calibration_status'


# ============================================================================
# CONNECTION HANDLERS
# ============================================================================

@socketio.on(WebSocketEvents.CONNECT)
def handle_connect():
    """Handle new WebSocket connection"""
    from flask import request
    session_id = request.sid
    print(f"[WebSocket] Client connected: {session_id}")
    emit('connection_status', {'status': 'connected', 'session_id': session_id})


@socketio.on(WebSocketEvents.DISCONNECT)
def handle_disconnect():
    """Handle WebSocket disconnection"""
    from flask import request
    session_id = request.sid
    
    # Remove from all user rooms
    for user_id, sessions in list(connected_users.items()):
        if session_id in sessions:
            sessions.discard(session_id)
            leave_room(f"user_{user_id}")
            if not sessions:
                del connected_users[user_id]
            print(f"[WebSocket] Client {session_id} disconnected from user {user_id}'s room")
    
    print(f"[WebSocket] Client disconnected: {session_id}")


@socketio.on(WebSocketEvents.JOIN_USER_ROOM)
def handle_join_user_room(data):
    """Join a user-specific room for personalized updates"""
    from flask import request
    
    user_id = str(data.get('user_id'))
    session_id = request.sid
    
    if not user_id:
        emit('error', {'message': 'user_id is required'})
        return
    
    # Join the user's room
    room_name = f"user_{user_id}"
    join_room(room_name)
    
    # Track the connection
    if user_id not in connected_users:
        connected_users[user_id] = set()
    connected_users[user_id].add(session_id)
    
    print(f"[WebSocket] Session {session_id} joined room: {room_name}")
    emit('room_joined', {
        'room': room_name,
        'user_id': user_id,
        'timestamp': datetime.now().isoformat()
    })


@socketio.on(WebSocketEvents.LEAVE_USER_ROOM)
def handle_leave_user_room(data):
    """Leave a user-specific room"""
    from flask import request
    
    user_id = str(data.get('user_id'))
    session_id = request.sid
    
    if user_id:
        room_name = f"user_{user_id}"
        leave_room(room_name)
        
        if user_id in connected_users:
            connected_users[user_id].discard(session_id)
            if not connected_users[user_id]:
                del connected_users[user_id]
        
        print(f"[WebSocket] Session {session_id} left room: {room_name}")
        emit('room_left', {'room': room_name, 'user_id': user_id})


# ============================================================================
# BROADCAST FUNCTIONS (Called from other parts of the app)
# ============================================================================

def broadcast_glucose_update(user_id: int, glucose_data: dict):
    """
    Broadcast a new glucose reading to all connected clients for a user.
    
    Args:
        user_id: The user's ID
        glucose_data: Dict containing glucose_value, timestamp, etc.
    """
    room_name = f"user_{user_id}"
    
    payload = {
        'type': 'glucose_update',
        'user_id': user_id,
        'data': {
            'glucose_value': glucose_data.get('glucose_value'),
            'timestamp': glucose_data.get('timestamp', datetime.now().isoformat()),
            'trend': glucose_data.get('trend', 'stable')
        },
        'server_time': datetime.now().isoformat()
    }
    
    socketio.emit(WebSocketEvents.GLUCOSE_UPDATE, payload, room=room_name)
    print(f"[WebSocket] Broadcast glucose update to room {room_name}: {glucose_data.get('glucose_value')} mg/dL")


def broadcast_prediction_update(user_id: int, prediction_data: dict):
    """
    Broadcast updated predictions to a user's connected clients.
    
    Args:
        user_id: The user's ID
        prediction_data: Dict containing prediction values
    """
    room_name = f"user_{user_id}"
    
    payload = {
        'type': 'prediction_update',
        'user_id': user_id,
        'data': {
            'predictions': prediction_data.get('adjusted_prediction', prediction_data.get('prediction', [])),
            'bounds': prediction_data.get('prediction_bounds'),
            'analysis': prediction_data.get('analysis'),
            'last_known_glucose': prediction_data.get('last_known_glucose')
        },
        'server_time': datetime.now().isoformat()
    }
    
    socketio.emit(WebSocketEvents.PREDICTION_UPDATE, payload, room=room_name)
    print(f"[WebSocket] Broadcast prediction update to room {room_name}")


def broadcast_health_score_update(user_id: int, health_score: dict):
    """
    Broadcast updated health score to a user's connected clients.
    
    Args:
        user_id: The user's ID
        health_score: Dict containing score, time_in_range, etc.
    """
    room_name = f"user_{user_id}"
    
    payload = {
        'type': 'health_score_update',
        'user_id': user_id,
        'data': health_score,
        'server_time': datetime.now().isoformat()
    }
    
    socketio.emit(WebSocketEvents.HEALTH_SCORE_UPDATE, payload, room=room_name)
    print(f"[WebSocket] Broadcast health score update to room {room_name}: {health_score.get('score')}")


def broadcast_alert(user_id: int, alert_type: str, message: str, severity: str = 'info'):
    """
    Send an alert to a user's connected clients.
    
    Args:
        user_id: The user's ID
        alert_type: Type of alert (hypo_warning, hyper_warning, meal_reminder, etc.)
        message: Alert message
        severity: Alert severity (info, warning, critical)
    """
    room_name = f"user_{user_id}"
    
    payload = {
        'type': 'alert',
        'user_id': user_id,
        'data': {
            'alert_type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        },
        'server_time': datetime.now().isoformat()
    }
    
    socketio.emit(WebSocketEvents.ALERT, payload, room=room_name)
    print(f"[WebSocket] Sent alert to room {room_name}: {alert_type} - {message}")


def broadcast_dashboard_refresh(user_id: int, reason: str = "data_updated"):
    """
    Signal clients to refresh dashboard data.
    
    Args:
        user_id: The user's ID
        reason: Reason for refresh (new_reading, meal_logged, etc.)
    """
    room_name = f"user_{user_id}"
    
    payload = {
        'type': 'dashboard_refresh',
        'user_id': user_id,
        'data': {
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        },
        'server_time': datetime.now().isoformat()
    }
    
    socketio.emit(WebSocketEvents.DASHBOARD_REFRESH, payload, room=room_name)
    print(f"[WebSocket] Sent dashboard refresh signal to room {room_name}: {reason}")


def broadcast_calibration_status(user_id: int, status: str, progress: int = 0, message: str = ""):
    """
    Send calibration progress updates to a user.
    
    Args:
        user_id: The user's ID
        status: Current status (started, training, completed, failed)
        progress: Progress percentage (0-100)
        message: Status message
    """
    room_name = f"user_{user_id}"
    
    payload = {
        'type': 'calibration_status',
        'user_id': user_id,
        'data': {
            'status': status,
            'progress': progress,
            'message': message,
            'timestamp': datetime.now().isoformat()
        },
        'server_time': datetime.now().isoformat()
    }
    
    socketio.emit(WebSocketEvents.CALIBRATION_STATUS, payload, room=room_name)
    print(f"[WebSocket] Sent calibration status to room {room_name}: {status} ({progress}%)")


# ============================================================================
# SMART ALERTS - Proactive notifications based on predictions
# ============================================================================

def check_and_send_proactive_alerts(user_id: int, prediction_data: dict, current_glucose: float):
    """
    Analyze predictions and send proactive alerts if needed.
    
    Args:
        user_id: The user's ID
        prediction_data: Prediction results
        current_glucose: Current glucose value
    """
    predictions = prediction_data.get('adjusted_prediction', [])
    
    if not predictions or len(predictions) < 6:
        return
    
    # Check for predicted hypoglycemia (low) in next hour
    min_predicted = min(predictions[:6])  # Next 30 minutes (6 x 5-min intervals)
    if min_predicted < 70:
        if min_predicted < 55:
            severity = 'critical'
            message = f"⚠️ URGENT: Glucose predicted to drop to {min_predicted} mg/dL within 30 minutes. Consider having fast-acting carbs NOW."
        else:
            severity = 'warning'
            message = f"⚠️ Low glucose alert: Predicted to reach {min_predicted} mg/dL. Consider a small snack."
        
        broadcast_alert(user_id, 'hypo_prediction', message, severity)
    
    # Check for predicted hyperglycemia
    max_predicted = max(predictions[:12])  # Next hour
    if max_predicted > 250 and current_glucose < 200:
        message = f"📈 Rising glucose: Predicted to reach {max_predicted} mg/dL. Consider activity or checking insulin timing."
        broadcast_alert(user_id, 'hyper_prediction', message, 'warning')
    
    # Check for rapid changes
    if len(predictions) >= 3:
        change_30min = predictions[5] - current_glucose if len(predictions) > 5 else 0
        if abs(change_30min) > 50:
            direction = "rise" if change_30min > 0 else "drop"
            message = f"🔄 Rapid glucose {direction} predicted: {abs(int(change_30min))} mg/dL change expected in 30 minutes."
            broadcast_alert(user_id, f'rapid_{direction}', message, 'info')


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_connected_users() -> Dict[str, int]:
    """Get count of connected sessions per user"""
    return {user_id: len(sessions) for user_id, sessions in connected_users.items()}


def is_user_connected(user_id: int) -> bool:
    """Check if a user has any connected clients"""
    return str(user_id) in connected_users and len(connected_users[str(user_id)]) > 0


def get_connection_stats() -> dict:
    """Get WebSocket connection statistics"""
    total_connections = sum(len(sessions) for sessions in connected_users.values())
    return {
        'total_connections': total_connections,
        'unique_users': len(connected_users),
        'users': get_connected_users()
    }
