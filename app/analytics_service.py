# file: analytics_service.py
# Advanced Analytics Service for Aura
# Includes AGP, GMI, CV, Pattern Analysis, and Time-of-Day Aware Predictions

import numpy as np
from scipy import stats
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import math

from cache_service import cache, cached_analytics


# ============================================================================
# CLINICAL METRICS CALCULATIONS
# ============================================================================

class ClinicalMetrics:
    """Calculate clinical-grade diabetes metrics"""
    
    # Target ranges (ADA guidelines)
    TARGET_LOW = 70  # mg/dL
    TARGET_HIGH = 180  # mg/dL
    TIGHT_LOW = 70
    TIGHT_HIGH = 140
    VERY_HIGH = 250
    VERY_LOW = 54
    
    @staticmethod
    def calculate_gmi(mean_glucose: float) -> float:
        """
        Calculate Glucose Management Indicator (GMI)
        GMI estimates A1C from mean glucose using the formula:
        GMI (%) = 3.31 + 0.02392 × [mean glucose in mg/dL]
        
        Source: Bergenstal et al., Diabetes Care 2018
        """
        if mean_glucose <= 0:
            return 0.0
        gmi = 3.31 + (0.02392 * mean_glucose)
        return round(gmi, 1)
    
    @staticmethod
    def calculate_cv(glucose_values: List[float]) -> float:
        """
        Calculate Coefficient of Variation (CV)
        CV = (Standard Deviation / Mean) × 100
        
        Clinical interpretation:
        - CV < 36%: Stable glucose
        - CV ≥ 36%: Unstable glucose (higher hypoglycemia risk)
        """
        if not glucose_values or len(glucose_values) < 2:
            return 0.0
        
        mean_val = np.mean(glucose_values)
        if mean_val == 0:
            return 0.0
        
        std_val = np.std(glucose_values)
        cv = (std_val / mean_val) * 100
        return round(cv, 1)
    
    @staticmethod
    def calculate_time_in_range(glucose_values: List[float]) -> Dict[str, float]:
        """
        Calculate Time in Range (TIR) and other range metrics
        
        Returns percentages for:
        - Very Low: < 54 mg/dL (Level 2 hypoglycemia)
        - Low: 54-69 mg/dL (Level 1 hypoglycemia)
        - In Range: 70-180 mg/dL
        - High: 181-250 mg/dL (Level 1 hyperglycemia)
        - Very High: > 250 mg/dL (Level 2 hyperglycemia)
        """
        if not glucose_values:
            return {
                "very_low": 0.0,
                "low": 0.0,
                "in_range": 0.0,
                "high": 0.0,
                "very_high": 0.0
            }
        
        total = len(glucose_values)
        
        very_low = sum(1 for v in glucose_values if v < 54) / total * 100
        low = sum(1 for v in glucose_values if 54 <= v < 70) / total * 100
        in_range = sum(1 for v in glucose_values if 70 <= v <= 180) / total * 100
        high = sum(1 for v in glucose_values if 180 < v <= 250) / total * 100
        very_high = sum(1 for v in glucose_values if v > 250) / total * 100
        
        return {
            "very_low": round(very_low, 1),
            "low": round(low, 1),
            "in_range": round(in_range, 1),
            "high": round(high, 1),
            "very_high": round(very_high, 1)
        }
    
    @staticmethod
    def calculate_glucose_risk_index(glucose_values: List[float]) -> Dict[str, float]:
        """
        Calculate Low Blood Glucose Index (LBGI) and High Blood Glucose Index (HBGI)
        
        These indices weight hypoglycemia and hyperglycemia asymmetrically,
        giving more weight to dangerous lows.
        
        Source: Kovatchev et al., Diabetes Technology & Therapeutics
        """
        if not glucose_values:
            return {"lbgi": 0.0, "hbgi": 0.0, "risk_category": "unknown"}
        
        lbgi_sum = 0.0
        hbgi_sum = 0.0
        
        for glucose in glucose_values:
            # Transform glucose to symmetric scale
            if glucose > 0:
                f_glucose = 1.509 * ((math.log(glucose) ** 1.084) - 5.381)
                
                # Risk function
                if f_glucose < 0:
                    lbgi_sum += 10 * (f_glucose ** 2)
                else:
                    hbgi_sum += 10 * (f_glucose ** 2)
        
        n = len(glucose_values)
        lbgi = lbgi_sum / n
        hbgi = hbgi_sum / n
        
        # Risk categorization
        if lbgi < 2.5 and hbgi < 5:
            risk_category = "low"
        elif lbgi < 5 and hbgi < 10:
            risk_category = "moderate"
        else:
            risk_category = "high"
        
        return {
            "lbgi": round(lbgi, 2),
            "hbgi": round(hbgi, 2),
            "risk_category": risk_category
        }


# ============================================================================
# AMBULATORY GLUCOSE PROFILE (AGP)
# ============================================================================

class AGPCalculator:
    """Generate Ambulatory Glucose Profile data"""
    
    @staticmethod
    def calculate_agp(readings: List[Dict], days: int = 14) -> Dict:
        """
        Calculate AGP percentile curves
        
        Groups glucose readings by time of day and calculates:
        - 5th percentile
        - 25th percentile
        - Median (50th percentile)
        - 75th percentile
        - 95th percentile
        
        Returns data points for every 15-minute interval across 24 hours
        """
        if not readings:
            return {"error": "No readings available"}
        
        # Group readings by 15-minute time slots (96 slots per day)
        time_buckets: Dict[int, List[float]] = defaultdict(list)
        
        for reading in readings:
            try:
                timestamp = reading.get('timestamp')
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
                # Calculate bucket (0-95 for 24 hours in 15-min intervals)
                minutes_from_midnight = timestamp.hour * 60 + timestamp.minute
                bucket = minutes_from_midnight // 15
                
                glucose = reading.get('glucose_value', 0)
                if glucose > 0:
                    time_buckets[bucket].append(glucose)
            except Exception:
                continue
        
        # Calculate percentiles for each bucket
        agp_data = {
            "time_labels": [],
            "median": [],
            "p25": [],
            "p75": [],
            "p10": [],
            "p90": [],
            "p5": [],
            "p95": []
        }
        
        for bucket in range(96):
            # Generate time label
            hours = (bucket * 15) // 60
            minutes = (bucket * 15) % 60
            time_label = f"{hours:02d}:{minutes:02d}"
            agp_data["time_labels"].append(time_label)
            
            values = time_buckets.get(bucket, [])
            
            if values and len(values) >= 3:
                agp_data["p5"].append(round(np.percentile(values, 5), 1))
                agp_data["p10"].append(round(np.percentile(values, 10), 1))
                agp_data["p25"].append(round(np.percentile(values, 25), 1))
                agp_data["median"].append(round(np.percentile(values, 50), 1))
                agp_data["p75"].append(round(np.percentile(values, 75), 1))
                agp_data["p90"].append(round(np.percentile(values, 90), 1))
                agp_data["p95"].append(round(np.percentile(values, 95), 1))
            else:
                # Interpolate or use None for missing data
                agp_data["p5"].append(None)
                agp_data["p10"].append(None)
                agp_data["p25"].append(None)
                agp_data["median"].append(None)
                agp_data["p75"].append(None)
                agp_data["p90"].append(None)
                agp_data["p95"].append(None)
        
        # Calculate summary statistics
        all_values = [v for values in time_buckets.values() for v in values]
        
        return {
            "agp_curves": agp_data,
            "summary": {
                "total_readings": len(all_values),
                "days_of_data": days,
                "mean_glucose": round(np.mean(all_values), 1) if all_values else 0,
                "gmi": ClinicalMetrics.calculate_gmi(np.mean(all_values) if all_values else 0),
                "cv": ClinicalMetrics.calculate_cv(all_values),
                "time_in_range": ClinicalMetrics.calculate_time_in_range(all_values)
            }
        }


# ============================================================================
# PATTERN ANALYSIS & TIME-OF-DAY AWARENESS
# ============================================================================

class PatternAnalyzer:
    """Analyze glucose patterns by time of day and detect anomalies"""
    
    # Time periods (based on physiological patterns)
    TIME_PERIODS = {
        "night": (0, 6),      # 12 AM - 6 AM
        "dawn": (6, 9),       # 6 AM - 9 AM (dawn phenomenon)
        "morning": (9, 12),   # 9 AM - 12 PM
        "afternoon": (12, 17), # 12 PM - 5 PM
        "evening": (17, 21),  # 5 PM - 9 PM
        "late_night": (21, 24) # 9 PM - 12 AM
    }
    
    # Meal time windows
    MEAL_WINDOWS = {
        "breakfast": (6, 10),
        "lunch": (11, 14),
        "dinner": (18, 21),
        "snacks": (14, 18)
    }
    
    @staticmethod
    def get_time_period(hour: int) -> str:
        """Get the time period name for a given hour"""
        for period, (start, end) in PatternAnalyzer.TIME_PERIODS.items():
            if start <= hour < end:
                return period
        return "night"
    
    @staticmethod
    def analyze_by_time_period(readings: List[Dict]) -> Dict[str, Dict]:
        """
        Analyze glucose patterns by time of day
        
        Returns statistics for each time period:
        - mean, median, std
        - min, max
        - time in range
        - trend (rising/falling/stable)
        """
        period_data: Dict[str, List[float]] = defaultdict(list)
        
        for reading in readings:
            try:
                timestamp = reading.get('timestamp')
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
                hour = timestamp.hour
                period = PatternAnalyzer.get_time_period(hour)
                
                glucose = reading.get('glucose_value', 0)
                if glucose > 0:
                    period_data[period].append(glucose)
            except Exception:
                continue
        
        results = {}
        for period, values in period_data.items():
            if values:
                results[period] = {
                    "mean": round(np.mean(values), 1),
                    "median": round(np.median(values), 1),
                    "std": round(np.std(values), 1),
                    "min": round(min(values), 1),
                    "max": round(max(values), 1),
                    "count": len(values),
                    "time_in_range": ClinicalMetrics.calculate_time_in_range(values)["in_range"],
                    "cv": ClinicalMetrics.calculate_cv(values)
                }
            else:
                results[period] = None
        
        return results
    
    @staticmethod
    def detect_dawn_phenomenon(readings: List[Dict]) -> Dict:
        """
        Detect Dawn Phenomenon (early morning glucose rise)
        
        Compares glucose levels:
        - Before dawn (3-5 AM): baseline
        - During dawn (5-8 AM): should rise 10-20 mg/dL naturally
        - Significant rise (>30 mg/dL): likely dawn phenomenon
        """
        pre_dawn_values = []
        dawn_values = []
        
        for reading in readings:
            try:
                timestamp = reading.get('timestamp')
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
                hour = timestamp.hour
                glucose = reading.get('glucose_value', 0)
                
                if glucose > 0:
                    if 3 <= hour < 5:
                        pre_dawn_values.append(glucose)
                    elif 5 <= hour < 8:
                        dawn_values.append(glucose)
            except Exception:
                continue
        
        if not pre_dawn_values or not dawn_values:
            return {
                "detected": False,
                "message": "Insufficient data to analyze dawn phenomenon",
                "pre_dawn_avg": None,
                "dawn_avg": None,
                "rise": None
            }
        
        pre_dawn_avg = np.mean(pre_dawn_values)
        dawn_avg = np.mean(dawn_values)
        rise = dawn_avg - pre_dawn_avg
        
        detected = rise > 30  # Significant rise indicates dawn phenomenon
        
        return {
            "detected": detected,
            "pre_dawn_avg": round(pre_dawn_avg, 1),
            "dawn_avg": round(dawn_avg, 1),
            "rise": round(rise, 1),
            "severity": "significant" if rise > 50 else "moderate" if rise > 30 else "normal",
            "recommendation": "Consider adjusting basal insulin or timing of long-acting insulin" if detected else "Dawn glucose patterns appear normal"
        }
    
    @staticmethod
    def generate_pattern_heatmap(readings: List[Dict]) -> Dict:
        """
        Generate heatmap data for glucose patterns
        
        Returns a 7x24 matrix (day of week × hour of day) with average glucose values
        """
        heatmap: Dict[int, Dict[int, List[float]]] = defaultdict(lambda: defaultdict(list))
        
        for reading in readings:
            try:
                timestamp = reading.get('timestamp')
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
                day_of_week = timestamp.weekday()  # 0 = Monday
                hour = timestamp.hour
                glucose = reading.get('glucose_value', 0)
                
                if glucose > 0:
                    heatmap[day_of_week][hour].append(glucose)
            except Exception:
                continue
        
        # Build the matrix
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        hours = list(range(24))
        
        matrix = []
        for day in range(7):
            row = []
            for hour in range(24):
                values = heatmap[day][hour]
                if values:
                    row.append(round(np.mean(values), 1))
                else:
                    row.append(None)
            matrix.append(row)
        
        return {
            "days": days,
            "hours": hours,
            "data": matrix,
            "color_scale": {
                "very_low": {"range": [0, 54], "color": "#ef4444"},
                "low": {"range": [54, 70], "color": "#f97316"},
                "target": {"range": [70, 140], "color": "#22c55e"},
                "above_target": {"range": [140, 180], "color": "#84cc16"},
                "high": {"range": [180, 250], "color": "#eab308"},
                "very_high": {"range": [250, 500], "color": "#dc2626"}
            }
        }
    
    @staticmethod
    def analyze_meal_impact(readings: List[Dict], meal_logs: List[Dict]) -> Dict:
        """
        Analyze how meals affect glucose levels
        
        For each meal, calculates:
        - Pre-meal glucose (30 min before)
        - Peak glucose (within 2 hours after)
        - Time to peak
        - Post-meal glucose (2 hours after)
        """
        if not readings or not meal_logs:
            return {"message": "Insufficient data for meal impact analysis"}
        
        # Convert readings to a time-indexed structure
        readings_by_time = {}
        for r in readings:
            try:
                ts = r.get('timestamp')
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                readings_by_time[ts] = r.get('glucose_value', 0)
            except Exception:
                continue
        
        meal_impacts = []
        
        for meal in meal_logs:
            try:
                meal_time = meal.get('timestamp')
                if isinstance(meal_time, str):
                    meal_time = datetime.fromisoformat(meal_time.replace('Z', '+00:00'))
                
                carbs = meal.get('carb_count', 0)
                description = meal.get('meal_description', 'Unknown')
                
                # Find readings around meal time
                pre_meal = None
                post_readings = []
                
                for ts, glucose in readings_by_time.items():
                    time_diff = (ts - meal_time).total_seconds() / 60  # minutes
                    
                    if -45 <= time_diff <= -15:
                        pre_meal = glucose
                    elif 0 < time_diff <= 150:  # Up to 2.5 hours after
                        post_readings.append((time_diff, glucose))
                
                if pre_meal and post_readings:
                    peak_reading = max(post_readings, key=lambda x: x[1])
                    post_2hr = min(post_readings, key=lambda x: abs(x[0] - 120)) if post_readings else None
                    
                    meal_impacts.append({
                        "meal_time": meal_time.isoformat(),
                        "description": description,
                        "carbs": carbs,
                        "pre_meal_glucose": pre_meal,
                        "peak_glucose": peak_reading[1],
                        "time_to_peak_min": round(peak_reading[0]),
                        "glucose_rise": round(peak_reading[1] - pre_meal, 1),
                        "post_2hr_glucose": post_2hr[1] if post_2hr else None
                    })
            except Exception:
                continue
        
        return {
            "meal_impacts": meal_impacts,
            "summary": {
                "avg_glucose_rise": round(np.mean([m["glucose_rise"] for m in meal_impacts]), 1) if meal_impacts else 0,
                "avg_time_to_peak": round(np.mean([m["time_to_peak_min"] for m in meal_impacts])) if meal_impacts else 0,
                "meals_analyzed": len(meal_impacts)
            }
        }


# ============================================================================
# TIME-OF-DAY AWARE PREDICTION ADJUSTMENTS
# ============================================================================

class CircadianAdjuster:
    """
    Apply circadian rhythm adjustments to glucose predictions
    Based on physiological patterns observed in diabetes research
    """
    
    # Typical circadian glucose variation factors (relative to baseline)
    # These are multipliers applied to predictions based on time of day
    CIRCADIAN_FACTORS = {
        0: 1.00,   # Midnight - stable
        1: 0.98,   # 1 AM - slightly lower
        2: 0.97,   # 2 AM - lowest (nocturnal dip)
        3: 0.98,   # 3 AM - starting to rise
        4: 1.00,   # 4 AM - dawn phenomenon begins
        5: 1.03,   # 5 AM - rising
        6: 1.06,   # 6 AM - dawn phenomenon peak
        7: 1.08,   # 7 AM - morning peak
        8: 1.05,   # 8 AM - post-breakfast typical
        9: 1.02,   # 9 AM - stabilizing
        10: 1.00,  # 10 AM - stable
        11: 0.99,  # 11 AM - pre-lunch dip possible
        12: 1.02,  # Noon - lunch effect
        13: 1.04,  # 1 PM - post-lunch rise
        14: 1.02,  # 2 PM - stabilizing
        15: 1.00,  # 3 PM - afternoon stable
        16: 0.99,  # 4 PM - slight dip
        17: 1.00,  # 5 PM - pre-dinner
        18: 1.02,  # 6 PM - dinner time
        19: 1.04,  # 7 PM - post-dinner rise
        20: 1.03,  # 8 PM - evening
        21: 1.02,  # 9 PM - winding down
        22: 1.01,  # 10 PM - nighttime begins
        23: 1.00,  # 11 PM - stable
    }
    
    # Insulin sensitivity varies by time of day (relative factor)
    INSULIN_SENSITIVITY = {
        "night": 1.2,      # More sensitive at night
        "dawn": 0.7,       # Less sensitive during dawn phenomenon
        "morning": 0.85,   # Moderately reduced sensitivity
        "afternoon": 1.0,  # Baseline
        "evening": 0.95,   # Slightly reduced
        "late_night": 1.1  # Increased sensitivity
    }
    
    @classmethod
    def adjust_predictions(cls, predictions: List[float], start_hour: int) -> List[float]:
        """
        Adjust prediction values based on time-of-day circadian factors
        
        Args:
            predictions: List of predicted glucose values (5-min intervals)
            start_hour: Hour of day when predictions start
        
        Returns:
            Adjusted prediction values
        """
        adjusted = []
        
        for i, pred in enumerate(predictions):
            # Calculate the hour for this prediction point
            # Assuming 5-minute intervals
            minutes_ahead = i * 5
            prediction_hour = (start_hour + (minutes_ahead // 60)) % 24
            
            # Get circadian factor for this hour
            factor = cls.CIRCADIAN_FACTORS.get(prediction_hour, 1.0)
            
            # Apply adjustment (small effect to avoid over-correction)
            adjustment = (factor - 1.0) * 0.5  # Dampen the effect
            adjusted_value = pred * (1 + adjustment)
            
            adjusted.append(round(adjusted_value, 1))
        
        return adjusted
    
    @classmethod
    def get_insulin_sensitivity_factor(cls, hour: int) -> float:
        """Get insulin sensitivity factor for a given hour"""
        period = PatternAnalyzer.get_time_period(hour)
        return cls.INSULIN_SENSITIVITY.get(period, 1.0)
    
    @classmethod
    def adjust_for_dawn_phenomenon(cls, predictions: List[float], start_hour: int, dawn_detected: bool, dawn_rise: float = 0) -> List[float]:
        """
        Apply additional dawn phenomenon adjustment if detected for this user
        
        Args:
            predictions: List of predicted glucose values
            start_hour: Hour when predictions start
            dawn_detected: Whether user has significant dawn phenomenon
            dawn_rise: Magnitude of user's typical dawn rise
        """
        if not dawn_detected or dawn_rise <= 30:
            return predictions
        
        adjusted = list(predictions)
        
        for i in range(len(adjusted)):
            minutes_ahead = i * 5
            prediction_hour = (start_hour + (minutes_ahead // 60)) % 24
            
            # Apply extra rise during dawn hours (5-8 AM)
            if 5 <= prediction_hour <= 8:
                # Scale based on user's typical dawn rise
                extra_rise = (dawn_rise - 30) * 0.3  # Dampened effect
                progress = (prediction_hour - 5) / 3  # 0 to 1 through dawn period
                dawn_adjustment = extra_rise * progress * 0.5
                adjusted[i] = round(adjusted[i] + dawn_adjustment, 1)
        
        return adjusted


# ============================================================================
# MAIN ANALYTICS FUNCTIONS (Called from API)
# ============================================================================

@cached_analytics("full_analytics")
def get_full_analytics(user_id: int, readings: List[Dict], meal_logs: List[Dict] = None, days: int = 7) -> Dict:
    """
    Generate comprehensive analytics for a user
    
    Returns:
        - Clinical metrics (GMI, CV, TIR)
        - AGP data
        - Pattern analysis
        - Dawn phenomenon detection
        - Heatmap data
    """
    if not readings:
        return {"error": "No readings available for analytics"}
    
    # Extract glucose values
    glucose_values = [r.get('glucose_value') for r in readings if r.get('glucose_value')]
    
    # Calculate all metrics
    clinical = {
        "mean_glucose": round(np.mean(glucose_values), 1),
        "gmi": ClinicalMetrics.calculate_gmi(np.mean(glucose_values)),
        "cv": ClinicalMetrics.calculate_cv(glucose_values),
        "time_in_range": ClinicalMetrics.calculate_time_in_range(glucose_values),
        "risk_indices": ClinicalMetrics.calculate_glucose_risk_index(glucose_values)
    }
    
    # Generate AGP
    agp = AGPCalculator.calculate_agp(readings, days)
    
    # Pattern analysis
    patterns = {
        "by_time_period": PatternAnalyzer.analyze_by_time_period(readings),
        "dawn_phenomenon": PatternAnalyzer.detect_dawn_phenomenon(readings),
        "heatmap": PatternAnalyzer.generate_pattern_heatmap(readings)
    }
    
    # Meal impact (if meal logs available)
    if meal_logs:
        patterns["meal_impact"] = PatternAnalyzer.analyze_meal_impact(readings, meal_logs)
    
    return {
        "clinical_metrics": clinical,
        "agp": agp,
        "patterns": patterns,
        "generated_at": datetime.now().isoformat(),
        "data_range_days": days,
        "total_readings": len(readings)
    }


# ============================================================================
# ADVANCED GLUCOSE ANALYTICS WRAPPER
# ============================================================================

class AdvancedGlucoseAnalytics:
    """
    Unified interface for advanced glucose analytics.
    Provides simplified methods for the analytics dashboard.
    """
    
    def __init__(self):
        self.clinical = ClinicalMetrics()
        self.agp_calculator = AGPCalculator()
        self.pattern_analyzer = PatternAnalyzer()
    
    def calculate_gmi(self, mean_glucose: float) -> float:
        """Calculate Glucose Management Indicator (GMI)."""
        return self.clinical.calculate_gmi(mean_glucose)
    
    def calculate_coefficient_of_variation(self, glucose_values: List[float]) -> float:
        """Calculate Coefficient of Variation (CV)."""
        return self.clinical.calculate_cv(glucose_values)
    
    def calculate_agp(self, readings: List[Dict], days: int = 7) -> Dict:
        """
        Calculate AGP for chart rendering.
        Returns simplified format for frontend Chart.js.
        """
        # Group readings by hour
        hourly_data: Dict[int, List[float]] = defaultdict(list)
        
        for reading in readings:
            try:
                timestamp = reading.get('timestamp')
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
                hour = timestamp.hour
                glucose = reading.get('glucose_value', 0)
                if glucose > 0:
                    hourly_data[hour].append(glucose)
            except Exception:
                continue
        
        if not any(hourly_data.values()):
            return None
        
        # Calculate percentiles per hour
        result = {
            "hours": list(range(24)),
            "median": [],
            "p10": [],
            "p25": [],
            "p75": [],
            "p90": []
        }
        
        for hour in range(24):
            values = hourly_data.get(hour, [])
            if values and len(values) >= 2:
                result["p10"].append(round(np.percentile(values, 10), 1))
                result["p25"].append(round(np.percentile(values, 25), 1))
                result["median"].append(round(np.percentile(values, 50), 1))
                result["p75"].append(round(np.percentile(values, 75), 1))
                result["p90"].append(round(np.percentile(values, 90), 1))
            else:
                # Use previous value or placeholder
                prev_idx = len(result["median"]) - 1
                if prev_idx >= 0:
                    result["p10"].append(result["p10"][prev_idx])
                    result["p25"].append(result["p25"][prev_idx])
                    result["median"].append(result["median"][prev_idx])
                    result["p75"].append(result["p75"][prev_idx])
                    result["p90"].append(result["p90"][prev_idx])
                else:
                    result["p10"].append(100)
                    result["p25"].append(110)
                    result["median"].append(120)
                    result["p75"].append(140)
                    result["p90"].append(160)
        
        return result
    
    def get_time_of_day_patterns(self, readings: List[Dict]) -> Dict[int, Dict]:
        """
        Get average glucose by hour for heatmap visualization.
        Returns: Dict mapping hour (0-23) to {avg: float, count: int}
        """
        hourly_data: Dict[int, List[float]] = defaultdict(list)
        
        for reading in readings:
            try:
                timestamp = reading.get('timestamp')
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
                hour = timestamp.hour
                glucose = reading.get('glucose_value', 0)
                if glucose > 0:
                    hourly_data[hour].append(glucose)
            except Exception:
                continue
        
        result = {}
        for hour in range(24):
            values = hourly_data.get(hour, [])
            if values:
                result[hour] = {
                    "avg": round(np.mean(values), 1),
                    "count": len(values),
                    "min": round(min(values), 1),
                    "max": round(max(values), 1)
                }
            else:
                result[hour] = {"avg": 120, "count": 0, "min": 120, "max": 120}
        
        return result
    
    def get_full_analysis(self, readings: List[Dict], meal_logs: List[Dict] = None, days: int = 7) -> Dict:
        """Get comprehensive analytics."""
        return get_full_analytics(0, readings, meal_logs, days)


def get_circadian_adjusted_predictions(predictions: List[float], user_id: int, readings: List[Dict]) -> List[float]:
    """
    Apply time-of-day adjustments to predictions
    
    Args:
        predictions: Raw prediction values from LSTM
        user_id: User ID for personalized adjustments
        readings: Historical readings for dawn phenomenon detection
    
    Returns:
        Circadian-adjusted prediction values
    """
    current_hour = datetime.now().hour
    
    # First apply general circadian adjustments
    adjusted = CircadianAdjuster.adjust_predictions(predictions, current_hour)
    
    # Check for dawn phenomenon
    dawn_analysis = PatternAnalyzer.detect_dawn_phenomenon(readings)
    if dawn_analysis.get("detected"):
        adjusted = CircadianAdjuster.adjust_for_dawn_phenomenon(
            adjusted, 
            current_hour, 
            True, 
            dawn_analysis.get("rise", 0)
        )
    
    return adjusted
