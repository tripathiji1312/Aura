# file: enhanced_natural_language_processor.py
import re
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import math

# --- Enhanced Food Database with Portions and Variations ---
FOOD_CARB_DATABASE = {
    # Grains & Starches (per typical serving)
    "pizza": {"carbs_per_serving": 30, "serving_size": "1 slice", "variations": ["slice of pizza", "pizza slice", "piece of pizza"]},
    "pasta": {"carbs_per_serving": 45, "serving_size": "1 cup cooked", "variations": ["spaghetti", "noodles", "macaroni"]},
    "rice": {"carbs_per_serving": 45, "serving_size": "1 cup cooked", "variations": ["white rice", "brown rice", "fried rice"]},
    "bread": {"carbs_per_serving": 15, "serving_size": "1 slice", "variations": ["toast", "slice of bread", "piece of bread"]},
    "sandwich": {"carbs_per_serving": 30, "serving_size": "1 sandwich", "variations": ["sub", "burger", "wrap"]},
    "bagel": {"carbs_per_serving": 45, "serving_size": "1 whole", "variations": ["everything bagel", "plain bagel"]},
    "cereal": {"carbs_per_serving": 30, "serving_size": "1 cup", "variations": ["breakfast cereal", "corn flakes"]},
    "oatmeal": {"carbs_per_serving": 30, "serving_size": "1 cup", "variations": ["porridge", "oats"]},
    
    # Fruits
    "apple": {"carbs_per_serving": 25, "serving_size": "1 medium", "variations": ["green apple", "red apple"]},
    "banana": {"carbs_per_serving": 30, "serving_size": "1 medium", "variations": ["ripe banana"]},
    "orange": {"carbs_per_serving": 20, "serving_size": "1 medium", "variations": ["citrus"]},
    "grapes": {"carbs_per_serving": 15, "serving_size": "1/2 cup", "variations": ["grape"]},
    "strawberries": {"carbs_per_serving": 8, "serving_size": "1 cup", "variations": ["strawberry", "berries"]},
    "blueberries": {"carbs_per_serving": 15, "serving_size": "1/2 cup", "variations": ["blueberry"]},
    
    # Beverages
    "coke": {"carbs_per_serving": 39, "serving_size": "12 oz can", "variations": ["coca cola", "cola", "soda"]},
    "diet coke": {"carbs_per_serving": 0, "serving_size": "12 oz can", "variations": ["diet cola", "diet soda"]},
    "coke zero": {"carbs_per_serving": 0, "serving_size": "12 oz can", "variations": ["zero cola"]},
    "orange juice": {"carbs_per_serving": 25, "serving_size": "8 oz", "variations": ["oj", "fruit juice"]},
    "milk": {"carbs_per_serving": 12, "serving_size": "8 oz", "variations": ["whole milk", "skim milk"]},
    "beer": {"carbs_per_serving": 13, "serving_size": "12 oz", "variations": ["lager", "ale"]},
    "wine": {"carbs_per_serving": 4, "serving_size": "5 oz", "variations": ["red wine", "white wine"]},
    
    # Vegetables
    "salad": {"carbs_per_serving": 5, "serving_size": "2 cups", "variations": ["green salad", "mixed greens"]},
    "potato": {"carbs_per_serving": 30, "serving_size": "1 medium", "variations": ["baked potato", "mashed potato", "fries", "french fries"]},
    "corn": {"carbs_per_serving": 15, "serving_size": "1/2 cup", "variations": ["sweet corn"]},
    "carrots": {"carbs_per_serving": 8, "serving_size": "1/2 cup", "variations": ["carrot"]},
    
    # Proteins (low carb)
    "chicken": {"carbs_per_serving": 0, "serving_size": "3 oz", "variations": ["grilled chicken", "chicken breast"]},
    "steak": {"carbs_per_serving": 0, "serving_size": "3 oz", "variations": ["beef", "meat"]},
    "fish": {"carbs_per_serving": 0, "serving_size": "3 oz", "variations": ["salmon", "tuna", "cod"]},
    "eggs": {"carbs_per_serving": 1, "serving_size": "2 eggs", "variations": ["egg", "scrambled eggs"]},
    
    # Desserts & Snacks
    "ice cream": {"carbs_per_serving": 30, "serving_size": "1/2 cup", "variations": ["icecream"]},
    "cake": {"carbs_per_serving": 35, "serving_size": "1 slice", "variations": ["piece of cake", "birthday cake"]},
    "cookie": {"carbs_per_serving": 8, "serving_size": "1 cookie", "variations": ["cookies", "biscuit"]},
    "chocolate": {"carbs_per_serving": 15, "serving_size": "1 oz", "variations": ["chocolate bar", "candy bar"]},
}

# Enhanced activity database with intensity and duration estimates
ACTIVITY_DATABASE = {
    # Light activities
    "walk": {"intensity": "light", "calories_per_min": 3, "variations": ["walking", "stroll"]},
    "yoga": {"intensity": "light", "calories_per_min": 2, "variations": ["stretching"]},
    
    # Moderate activities  
    "jog": {"intensity": "moderate", "calories_per_min": 8, "variations": ["jogging", "light run"]},
    "bike": {"intensity": "moderate", "calories_per_min": 6, "variations": ["cycling", "bicycle", "biking"]},
    "swim": {"intensity": "moderate", "calories_per_min": 7, "variations": ["swimming", "pool"]},
    "dance": {"intensity": "moderate", "calories_per_min": 5, "variations": ["dancing"]},
    
    # Vigorous activities
    "run": {"intensity": "vigorous", "calories_per_min": 12, "variations": ["running", "sprint"]},
    "gym": {"intensity": "vigorous", "calories_per_min": 8, "variations": ["workout", "exercise", "training", "lift", "weights"]},
    "basketball": {"intensity": "vigorous", "calories_per_min": 10, "variations": ["ball", "sports"]},
    "soccer": {"intensity": "vigorous", "calories_per_min": 9, "variations": ["football", "sport"]},
}

# Quantity mapping words to numbers
QUANTITY_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "a": 1, "an": 1, "single": 1, "couple": 2, "few": 3, "several": 4,
    "half": 0.5, "quarter": 0.25, "third": 0.33
}

# Time-related keywords
TIME_KEYWORDS = {
    "breakfast": {"time": 7, "meal_type": "breakfast"},
    "lunch": {"time": 12, "meal_type": "lunch"}, 
    "dinner": {"time": 19, "meal_type": "dinner"},
    "snack": {"time": None, "meal_type": "snack"},
    "morning": {"time": 8, "meal_type": "morning"},
    "evening": {"time": 18, "meal_type": "evening"},
    "tonight": {"time": 19, "meal_type": "evening"},
    "now": {"time": None, "meal_type": "current"},
    "later": {"time": None, "meal_type": "future"},
}

# (Keep all your database definitions at the top of the file the same)

class EnhancedNLPProcessor:
    """
    Advanced Natural Language Processor for diabetes management
    Handles complex food descriptions, quantities, activities, and timing
    """
    
    def __init__(self):
        self.food_db = FOOD_CARB_DATABASE
        self.activity_db = ACTIVITY_DATABASE
        self.quantity_words = QUANTITY_WORDS
        self.time_keywords = TIME_KEYWORDS
        
        self.food_variations = {}
        self.activity_variations = {}
        # Sort food variations by length (longest first) to fix substring bugs
        self._sorted_food_keys = sorted(self.food_variations.keys(), key=len, reverse=True)
        self._build_variation_maps()

    def _build_variation_maps(self):
        for food, data in self.food_db.items():
            self.food_variations[food.lower()] = food
            for variation in data.get("variations", []):
                self.food_variations[variation.lower()] = food
        
        for activity, data in self.activity_db.items():
            self.activity_variations[activity.lower()] = activity
            for variation in data.get("variations", []):
                self.activity_variations[variation.lower()] = activity
        
        # ** FIX **: Sort the keys by length, descending. This is crucial.
        self._sorted_food_keys = sorted(self.food_variations.keys(), key=len, reverse=True)

    def parse_user_text(self, text: str) -> Dict:
        lower_text = text.lower().strip()
        
        entities = {
            "carbs": 0, "foods_detected": [], "activities_detected": [], "timing": None,
            "confidence": 0.0, "original_text": text, "warnings": [], "meal_type": None
        }
        
        entities.update(self._extract_timing(lower_text))
        
        # ** FIX **: The new, more robust extraction method
        food_results, remaining_text = self._extract_foods_with_quantities(lower_text)
        entities["carbs"] = food_results["total_carbs"]
        entities["foods_detected"] = food_results["foods"]
        
        explicit_carbs = self._extract_explicit_carbs(lower_text)
        if explicit_carbs > 0:
            entities["carbs"] = explicit_carbs
            entities["warnings"].append("Used explicit carb amount, ignoring food estimates")
        
        # Pass the remaining text so we don't confuse food numbers with activity durations
        entities["activities_detected"] = self._extract_activities(remaining_text)
        
        entities["confidence"] = self._calculate_confidence(entities, lower_text)
        
        return entities

    def _extract_foods_with_quantities(self, text: str) -> Tuple[Dict, str]:
        foods_found = []
        total_carbs = 0
        text_copy = " " + text + " " # Pad text for easier regex matching at edges

        for pattern in self._sorted_food_keys:
            # Use regex to find whole words to avoid matching 'apple' in 'grapple'
            pattern_regex = r'\b' + re.escape(pattern) + r'\b'
            
            # Find all occurrences of the pattern in the text
            for match in re.finditer(pattern_regex, text_copy):
                start_pos = match.start()
                
                # Check if this position has already been processed
                if text_copy[start_pos] == '#':
                    continue

                main_food_key = self.food_variations[pattern]
                food_data = self.food_db[main_food_key]
                
                quantity = self._find_quantity_near_food(text_copy, start_pos)
                carbs = food_data["carbs_per_serving"] * quantity
                
                foods_found.append({
                    "food": main_food_key, "quantity": quantity, "carbs": carbs,
                    "serving_size": food_data["serving_size"], "matched_pattern": pattern
                })
                
                total_carbs += carbs
                
                # ** FIX **: "Block out" the matched food to prevent re-matching
                text_copy = text_copy[:start_pos] + "#" * len(pattern) + text_copy[match.end():]
        
        return {"foods": foods_found, "total_carbs": total_carbs}, text_copy

    def _find_quantity_near_food(self, text: str, food_pos: int) -> float:
        # ** FIX **: Search in a much smaller, more specific window BEFORE the food
        window_text = text[max(0, food_pos - 20):food_pos]
        
        # Look for number patterns like "2 ", "3.5 ", "two "
        number_match = re.search(r'(\d+(?:\.\d+)?)\s*$', window_text)
        if number_match:
            try:
                return float(number_match.group(1))
            except (ValueError, IndexError):
                pass
        
        for word, value in self.quantity_words.items():
            # Use word boundaries for more precise matching
            if re.search(r'\b' + word + r'\b\s*$', window_text):
                return value
        
        return 1.0 # Default to a single serving

    # (The rest of your functions: _extract_explicit_carbs, _extract_activities, etc., can remain the same)
    # ... PASTE THE REST OF YOUR CLASS FUNCTIONS HERE ...
    def _extract_explicit_carbs(self, text: str) -> int:
        # ... (no changes needed)
        patterns = [
            r'(\d+)\s*(?:g|grams?)\s*(?:of\s*)?carbs?',
            r'(\d+)\s*carbs?\s*(?:g|grams?)',
            r'(\d+)\s*(?:g|grams?)\s*carbohydrates?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        
        return 0

    def _extract_activities(self, text: str) -> List[Dict]:
        # ... (no changes needed)
        activities = []
        
        for activity_key, activity_data in self.activity_db.items():
            patterns_to_check = [activity_key] + activity_data.get("variations", [])
            
            for pattern in patterns_to_check:
                if pattern in text:
                    duration = self._extract_duration_near_activity(text, pattern)
                    
                    activities.append({
                        "activity": activity_key,
                        "intensity": activity_data["intensity"],
                        "duration_minutes": duration,
                        "calories_estimate": duration * activity_data["calories_per_min"],
                        "matched_pattern": pattern
                    })
                    break
        
        return activities

    def _extract_duration_near_activity(self, text: str, activity_pattern: str) -> int:
        # ... (no changes needed)
        activity_pos = text.find(activity_pattern)
        if activity_pos == -1:
            return 30  # Default 30 minutes
        
        window_start = max(0, activity_pos - 20)
        window_end = min(len(text), activity_pos + len(activity_pattern) + 20)
        window_text = text[window_start:window_end]
        
        duration_patterns = [
            r'(\d+)\s*(?:minutes?|mins?)',
            r'(\d+)\s*(?:hours?|hrs?)',
            r'(\d+)\s*h',
            r'(\d+)\s*m',
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, window_text)
            if match:
                value = int(match.group(1))
                if 'hour' in pattern or 'hr' in pattern or 'h' in pattern:
                    return value * 60
                return value
        
        activity_info = self.activity_db.get(self.activity_variations.get(activity_pattern, ""), {})
        intensity = activity_info.get("intensity", "moderate")
        
        if intensity == "light": return 45
        elif intensity == "moderate": return 30
        else: return 25

    def _extract_timing(self, text: str) -> Dict:
        # ... (no changes needed)
        timing_info = {"timing": None, "meal_type": None}
        
        for keyword, data in self.time_keywords.items():
            if keyword in text:
                timing_info["timing"] = data["time"]
                timing_info["meal_type"] = data["meal_type"]
                break
        
        return timing_info

    def _calculate_confidence(self, entities: Dict, text: str) -> float:
        # ... (no changes needed)
        confidence = 0.0
        if entities["foods_detected"]: confidence += 0.4
        if entities["carbs"] > 0 and ("g" in text or "gram" in text): confidence += 0.3
        if entities["activities_detected"]: confidence += 0.2
        if entities["meal_type"]: confidence += 0.1
        if len(text.split()) < 3: confidence *= 0.8
        return min(confidence, 1.0)

    def get_insulin_adjustment_suggestion(self, entities: Dict) -> Dict:
        # ... (no changes needed)
        suggestions = {
            "carb_bolus_needed": False, "exercise_reduction": False,
            "timing_considerations": [], "estimated_carb_bolus": 0,
            "exercise_reduction_percent": 0
        }
        
        if entities["carbs"] > 5:
            suggestions["carb_bolus_needed"] = True
            suggestions["estimated_carb_bolus"] = round(entities["carbs"] / 12, 1)
        
        if entities["activities_detected"]:
            for activity in entities["activities_detected"]:
                if activity["intensity"] in ["moderate", "vigorous"]:
                    suggestions["exercise_reduction"] = True
                    suggestions["exercise_reduction_percent"] = 25 if activity["intensity"] == "vigorous" else 15
        
        if entities["meal_type"] == "breakfast":
            suggestions["timing_considerations"].append("Consider dawn phenomenon - may need extra insulin")
        elif entities["meal_type"] == "evening":
            suggestions["timing_considerations"].append("Evening meals may affect overnight glucose")
        
        return suggestions
# --- Enhanced Testing and Usage Examples ---
# def run_comprehensive_tests():
#     """Run comprehensive tests of the enhanced NLP processor"""
#     processor = EnhancedNLPProcessor()
    
#     test_cases = [
#         # Basic food detection
#         "I had two slices of pizza for lunch",
#         "Thinking about a sandwich and an apple",
#         "Just drank a coke and ate 3 cookies",
        
#         # Explicit carb amounts
#         "I ate 65g of carbs for dinner",
#         "Had about 45 grams carbs with breakfast",
        
#         # Complex food descriptions
#         "Large coffee with milk, whole grain toast with jam, and orange juice",
#         "Grilled chicken salad with no dressing",
#         "Had pasta with meat sauce and a glass of wine",
        
#         # Activities with duration
#         "Going for a 45 minute walk after dinner",
#         "Just finished a 2 hour gym session",
#         "Quick 15 minute jog this morning",
        
#         # Combined scenarios
#         "Had breakfast (oatmeal and banana) then went for a 30 min bike ride",
#         "Planning pizza for lunch then basketball practice for 1 hour",
        
#         # Edge cases
#         "Nothing but water today",
#         "Steak and vegetables, no carbs",
#         "Diet coke and sugar-free gum",
#     ]
    
#     print("=== ENHANCED NLP PROCESSOR TEST RESULTS ===\n")
    
#     for i, text in enumerate(test_cases, 1):
#         print(f"Test {i}: '{text}'")
#         result = processor.parse_user_text(text)
        
#         print(f"  📊 Carbs: {result['carbs']}g (confidence: {result['confidence']:.1%})")
        
#         if result['foods_detected']:
#             print(f"  🍽️  Foods: {[f'{f['quantity']}x {f['food']} ({f['carbs']}g)' for f in result['foods_detected']]}")
        
#         if result['activities_detected']:
#             activities_str = [f"{a['activity']} ({a['duration_minutes']}min, {a['intensity']})" 
#                             for a in result['activities_detected']]
#             print(f"  🏃 Activities: {activities_str}")
        
#         if result['meal_type']:
#             print(f"  🕐 Meal Context: {result['meal_type']}")
        
#         if result['warnings']:
#             print(f"  ⚠️  Warnings: {result['warnings']}")
        
#         # Get insulin suggestions
#         suggestions = processor.get_insulin_adjustment_suggestion(result)
#         if suggestions['carb_bolus_needed'] or suggestions['exercise_reduction']:
#             print(f"  💉 Insulin Suggestions:")
#             if suggestions['carb_bolus_needed']:
#                 print(f"     • Carb bolus: ~{suggestions['estimated_carb_bolus']} units")
#             if suggestions['exercise_reduction']:
#                 print(f"     • Reduce insulin by {suggestions['exercise_reduction_percent']}% for exercise")
        
#         print()

# if __name__ == '__main__':
#     run_comprehensive_tests()
# --- Interactive Testing Loop ---

def interactive_test():
    """Creates a simple command-line interface to test the NLP processor."""
    
    # Initialize one instance of your powerful NLP processor
    processor = EnhancedNLPProcessor()
    
    print("=" * 50)
    print("  Aura Natural Language Processor - Interactive Test")
    print("=" * 50)
    print("Enter a sentence to see how the AI understands it.")
    print("Type 'quit' or 'exit' to stop.")
    
    # This loop will run forever until you type 'quit'
    while True:
        # 1. Get input from you
        text = input("\nEnter your sentence > ")
        
        # 2. Check if the user wants to exit
        if text.lower() in ['quit', 'exit']:
            print("Exiting test mode. Goodbye!")
            break
            
        # 3. Process the text using your class
        result = processor.parse_user_text(text)
        
        # 4. Print a detailed, easy-to-read report
        print("\n--- AI Analysis ---")
        print(f"  📊 Total Carbs Detected: {result['carbs']}g (Confidence: {result['confidence']:.1%})")
        
        if result['foods_detected']:
            print("  🍽️  Foods Identified:")
            for food in result['foods_detected']:
                print(f"     - {food['quantity']}x {food['food']} ({food['carbs']}g)")
        else:
            print("  🍽️  Foods Identified: None")
            
        if result['activities_detected']:
            print("  🏃 Activities Identified:")
            for activity in result['activities_detected']:
                print(f"     - {activity['activity']} ({activity['duration_minutes']}min, intensity: {activity['intensity']})")
        else:
            print("  🏃 Activities Identified: None")
            
        if result['meal_type']:
            print(f"  🕐 Meal Context: {result['meal_type']}")
        
        if result['warnings']:
            print(f"  ⚠️  Warnings: {result['warnings']}")
        
        print("--------------------")

# This is the standard Python entry point.
# It tells the script to run the interactive_test() function
# when you execute `python natural_language_processor.py`.
if __name__ == '__main__':
    interactive_test()