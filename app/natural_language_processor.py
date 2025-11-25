# file: natural_language_processor.py
# Enhanced NLP for comprehensive health management
import re
from typing import Dict, List, Tuple

# ============================================================================
# COMPREHENSIVE FOOD DATABASE - Indian & International Foods
# ============================================================================
FOOD_CARB_DATABASE = {
    # === GRAINS & STARCHES ===
    "pizza": {"carbs_per_serving": 30, "serving_size": "1 slice", "gi": "high", "category": "fast_food",
              "variations": ["slice of pizza", "pizza slice", "piece of pizza", "dominos", "pizza hut"]},
    "pasta": {"carbs_per_serving": 45, "serving_size": "1 cup cooked", "gi": "medium", "category": "grain",
              "variations": ["spaghetti", "noodles", "macaroni", "penne", "lasagna", "fettuccine"]},
    "rice": {"carbs_per_serving": 45, "serving_size": "1 cup cooked", "gi": "high", "category": "grain",
             "variations": ["white rice", "brown rice", "fried rice", "steamed rice", "basmati", "jasmine rice", "chawal"]},
    "bread": {"carbs_per_serving": 15, "serving_size": "1 slice", "gi": "high", "category": "grain",
              "variations": ["toast", "slice of bread", "piece of bread", "white bread", "brown bread", "whole wheat bread"]},
    "roti": {"carbs_per_serving": 18, "serving_size": "1 piece", "gi": "medium", "category": "grain",
             "variations": ["chapati", "chapatti", "phulka", "indian bread", "wheat roti"]},
    "naan": {"carbs_per_serving": 45, "serving_size": "1 piece", "gi": "high", "category": "grain",
             "variations": ["butter naan", "garlic naan", "tandoori naan"]},
    "paratha": {"carbs_per_serving": 30, "serving_size": "1 piece", "gi": "medium", "category": "grain",
                "variations": ["aloo paratha", "gobi paratha", "paneer paratha", "stuffed paratha"]},
    "dosa": {"carbs_per_serving": 35, "serving_size": "1 piece", "gi": "medium", "category": "grain",
             "variations": ["masala dosa", "plain dosa", "rava dosa", "onion dosa", "paper dosa"]},
    "idli": {"carbs_per_serving": 12, "serving_size": "1 piece", "gi": "medium", "category": "grain",
             "variations": ["idly", "rava idli", "steamed idli"]},
    "poha": {"carbs_per_serving": 25, "serving_size": "1 cup", "gi": "medium", "category": "grain",
             "variations": ["flattened rice", "beaten rice", "chivda"]},
    "upma": {"carbs_per_serving": 30, "serving_size": "1 cup", "gi": "medium", "category": "grain",
             "variations": ["rava upma", "semolina upma"]},
    "biryani": {"carbs_per_serving": 60, "serving_size": "1 plate", "gi": "high", "category": "grain",
                "variations": ["chicken biryani", "mutton biryani", "veg biryani", "hyderabadi biryani", "dum biryani"]},
    "pulao": {"carbs_per_serving": 50, "serving_size": "1 plate", "gi": "high", "category": "grain",
              "variations": ["veg pulao", "pulav", "pilaf"]},
    "sandwich": {"carbs_per_serving": 30, "serving_size": "1 sandwich", "gi": "medium", "category": "fast_food",
                 "variations": ["sub", "wrap", "club sandwich", "grilled sandwich"]},
    "burger": {"carbs_per_serving": 35, "serving_size": "1 burger", "gi": "high", "category": "fast_food",
               "variations": ["hamburger", "cheeseburger", "veggie burger", "mcdonalds", "kfc burger"]},
    "bagel": {"carbs_per_serving": 45, "serving_size": "1 whole", "gi": "high", "category": "grain",
              "variations": ["everything bagel", "plain bagel"]},
    "cereal": {"carbs_per_serving": 30, "serving_size": "1 cup", "gi": "high", "category": "grain",
               "variations": ["breakfast cereal", "corn flakes", "muesli", "granola", "oats cereal"]},
    "oatmeal": {"carbs_per_serving": 27, "serving_size": "1 cup", "gi": "low", "category": "grain",
                "variations": ["porridge", "oats", "rolled oats", "steel cut oats", "overnight oats"]},
    "quinoa": {"carbs_per_serving": 35, "serving_size": "1 cup", "gi": "low", "category": "grain",
               "variations": ["quinoa salad", "quinoa bowl"]},
    
    # === FRUITS ===
    "apple": {"carbs_per_serving": 25, "serving_size": "1 medium", "gi": "low", "category": "fruit",
              "variations": ["green apple", "red apple", "seb"]},
    "banana": {"carbs_per_serving": 27, "serving_size": "1 medium", "gi": "medium", "category": "fruit",
               "variations": ["ripe banana", "kela", "plantain"]},
    "mango": {"carbs_per_serving": 25, "serving_size": "1 cup", "gi": "medium", "category": "fruit",
              "variations": ["aam", "alphonso", "mango shake", "mango juice"]},
    "orange": {"carbs_per_serving": 15, "serving_size": "1 medium", "gi": "low", "category": "fruit",
               "variations": ["citrus", "santra", "mandarin"]},
    "grapes": {"carbs_per_serving": 15, "serving_size": "1/2 cup", "gi": "medium", "category": "fruit",
               "variations": ["grape", "angoor", "green grapes", "black grapes"]},
    "watermelon": {"carbs_per_serving": 12, "serving_size": "1 cup", "gi": "high", "category": "fruit",
                   "variations": ["tarbooz", "melon"]},
    "papaya": {"carbs_per_serving": 15, "serving_size": "1 cup", "gi": "medium", "category": "fruit",
               "variations": ["papita", "paw paw"]},
    "pomegranate": {"carbs_per_serving": 20, "serving_size": "1/2 cup", "gi": "low", "category": "fruit",
                    "variations": ["anar", "pomegranate juice"]},
    "strawberries": {"carbs_per_serving": 8, "serving_size": "1 cup", "gi": "low", "category": "fruit",
                     "variations": ["strawberry", "berries"]},
    "blueberries": {"carbs_per_serving": 15, "serving_size": "1/2 cup", "gi": "low", "category": "fruit",
                    "variations": ["blueberry"]},
    "pineapple": {"carbs_per_serving": 20, "serving_size": "1 cup", "gi": "medium", "category": "fruit",
                  "variations": ["ananas"]},
    "guava": {"carbs_per_serving": 8, "serving_size": "1 medium", "gi": "low", "category": "fruit",
              "variations": ["amrood", "guavas"]},
    
    # === BEVERAGES ===
    "coke": {"carbs_per_serving": 39, "serving_size": "12 oz can", "gi": "high", "category": "beverage",
             "variations": ["coca cola", "cola", "soda", "pepsi", "sprite", "fanta", "soft drink", "cold drink"]},
    "diet coke": {"carbs_per_serving": 0, "serving_size": "12 oz can", "gi": "none", "category": "beverage",
                  "variations": ["diet cola", "diet soda", "coke zero", "zero sugar", "sugar free drink"]},
    "orange juice": {"carbs_per_serving": 25, "serving_size": "8 oz", "gi": "high", "category": "beverage",
                     "variations": ["oj", "fruit juice", "fresh juice", "tropicana"]},
    "apple juice": {"carbs_per_serving": 28, "serving_size": "8 oz", "gi": "high", "category": "beverage",
                    "variations": ["apple drink"]},
    "milk": {"carbs_per_serving": 12, "serving_size": "8 oz", "gi": "low", "category": "beverage",
             "variations": ["whole milk", "skim milk", "dudh", "full cream milk", "toned milk"]},
    "lassi": {"carbs_per_serving": 25, "serving_size": "1 glass", "gi": "medium", "category": "beverage",
              "variations": ["sweet lassi", "mango lassi", "salted lassi", "chaas"]},
    "chai": {"carbs_per_serving": 8, "serving_size": "1 cup", "gi": "low", "category": "beverage",
             "variations": ["tea", "indian tea", "masala chai", "cutting chai", "ginger tea"]},
    "coffee": {"carbs_per_serving": 0, "serving_size": "1 cup black", "gi": "none", "category": "beverage",
               "variations": ["black coffee", "espresso", "americano"]},
    "latte": {"carbs_per_serving": 15, "serving_size": "12 oz", "gi": "low", "category": "beverage",
              "variations": ["cafe latte", "cappuccino", "mocha", "frappe"]},
    "smoothie": {"carbs_per_serving": 35, "serving_size": "12 oz", "gi": "medium", "category": "beverage",
                 "variations": ["fruit smoothie", "protein shake", "milkshake", "shake"]},
    "beer": {"carbs_per_serving": 13, "serving_size": "12 oz", "gi": "high", "category": "beverage",
             "variations": ["lager", "ale", "kingfisher", "budweiser"]},
    "wine": {"carbs_per_serving": 4, "serving_size": "5 oz", "gi": "low", "category": "beverage",
             "variations": ["red wine", "white wine"]},
    "coconut water": {"carbs_per_serving": 10, "serving_size": "1 cup", "gi": "low", "category": "beverage",
                      "variations": ["nariyal pani", "tender coconut"]},
    
    # === VEGETABLES (Low Carb) ===
    "salad": {"carbs_per_serving": 5, "serving_size": "2 cups", "gi": "low", "category": "vegetable",
              "variations": ["green salad", "mixed greens", "garden salad", "kachumber"]},
    "potato": {"carbs_per_serving": 30, "serving_size": "1 medium", "gi": "high", "category": "vegetable",
               "variations": ["baked potato", "mashed potato", "fries", "french fries", "aloo", "chips"]},
    "sweet potato": {"carbs_per_serving": 25, "serving_size": "1 medium", "gi": "medium", "category": "vegetable",
                     "variations": ["shakarkandi", "yam"]},
    "corn": {"carbs_per_serving": 15, "serving_size": "1/2 cup", "gi": "medium", "category": "vegetable",
             "variations": ["sweet corn", "bhutta", "makka"]},
    "peas": {"carbs_per_serving": 12, "serving_size": "1/2 cup", "gi": "low", "category": "vegetable",
             "variations": ["green peas", "matar"]},
    "carrots": {"carbs_per_serving": 8, "serving_size": "1/2 cup", "gi": "low", "category": "vegetable",
                "variations": ["carrot", "gajar"]},
    "beans": {"carbs_per_serving": 8, "serving_size": "1/2 cup", "gi": "low", "category": "vegetable",
              "variations": ["green beans", "string beans", "french beans"]},
    "broccoli": {"carbs_per_serving": 4, "serving_size": "1 cup", "gi": "low", "category": "vegetable",
                 "variations": ["steamed broccoli"]},
    "spinach": {"carbs_per_serving": 1, "serving_size": "1 cup", "gi": "low", "category": "vegetable",
                "variations": ["palak", "saag"]},
    "cauliflower": {"carbs_per_serving": 3, "serving_size": "1 cup", "gi": "low", "category": "vegetable",
                    "variations": ["gobi", "phool gobi"]},
    
    # === PROTEINS (Very Low Carb) ===
    "chicken": {"carbs_per_serving": 0, "serving_size": "100g", "gi": "none", "category": "protein",
                "variations": ["grilled chicken", "chicken breast", "tandoori chicken", "butter chicken", 
                              "chicken curry", "chicken tikka", "fried chicken"]},
    "mutton": {"carbs_per_serving": 0, "serving_size": "100g", "gi": "none", "category": "protein",
               "variations": ["lamb", "goat meat", "mutton curry", "rogan josh", "keema"]},
    "fish": {"carbs_per_serving": 0, "serving_size": "100g", "gi": "none", "category": "protein",
             "variations": ["salmon", "tuna", "cod", "fish curry", "fish fry", "machli", "pomfret", "rohu"]},
    "prawns": {"carbs_per_serving": 0, "serving_size": "100g", "gi": "none", "category": "protein",
               "variations": ["shrimp", "jhinga", "prawn curry"]},
    "eggs": {"carbs_per_serving": 1, "serving_size": "2 eggs", "gi": "none", "category": "protein",
             "variations": ["egg", "scrambled eggs", "omelette", "omelet", "boiled egg", "fried egg", "anda", "egg bhurji"]},
    "paneer": {"carbs_per_serving": 3, "serving_size": "100g", "gi": "none", "category": "protein",
               "variations": ["cottage cheese", "paneer tikka", "shahi paneer", "palak paneer", "paneer butter masala"]},
    "tofu": {"carbs_per_serving": 2, "serving_size": "100g", "gi": "none", "category": "protein",
             "variations": ["soya paneer", "bean curd"]},
    "dal": {"carbs_per_serving": 20, "serving_size": "1 cup", "gi": "low", "category": "protein",
            "variations": ["lentils", "daal", "toor dal", "moong dal", "masoor dal", "chana dal", "dal tadka", "dal fry"]},
    "rajma": {"carbs_per_serving": 22, "serving_size": "1 cup", "gi": "low", "category": "protein",
              "variations": ["kidney beans", "rajma chawal"]},
    "chole": {"carbs_per_serving": 25, "serving_size": "1 cup", "gi": "low", "category": "protein",
              "variations": ["chickpeas", "chana", "chana masala", "chole bhature"]},
    "steak": {"carbs_per_serving": 0, "serving_size": "6 oz", "gi": "none", "category": "protein",
              "variations": ["beef", "beef steak", "ribeye"]},
    
    # === INDIAN DISHES ===
    "samosa": {"carbs_per_serving": 25, "serving_size": "1 piece", "gi": "high", "category": "snack",
               "variations": ["aloo samosa", "veg samosa"]},
    "pakora": {"carbs_per_serving": 15, "serving_size": "4 pieces", "gi": "high", "category": "snack",
               "variations": ["pakoda", "bhajiya", "onion pakora", "paneer pakora"]},
    "vada": {"carbs_per_serving": 20, "serving_size": "2 pieces", "gi": "high", "category": "snack",
             "variations": ["medu vada", "batata vada", "dahi vada"]},
    "pav bhaji": {"carbs_per_serving": 55, "serving_size": "1 plate", "gi": "high", "category": "fast_food",
                  "variations": ["pao bhaji"]},
    "pani puri": {"carbs_per_serving": 30, "serving_size": "6 pieces", "gi": "high", "category": "snack",
                  "variations": ["golgappa", "puchka", "gol gappa"]},
    "chaat": {"carbs_per_serving": 35, "serving_size": "1 plate", "gi": "high", "category": "snack",
              "variations": ["bhel puri", "sev puri", "papdi chaat", "aloo chaat", "dahi puri"]},
    "kachori": {"carbs_per_serving": 30, "serving_size": "1 piece", "gi": "high", "category": "snack",
                "variations": ["dal kachori", "pyaaz kachori"]},
    "thali": {"carbs_per_serving": 80, "serving_size": "1 thali", "gi": "high", "category": "meal",
              "variations": ["gujarati thali", "rajasthani thali", "south indian thali", "north indian thali"]},
    "khichdi": {"carbs_per_serving": 35, "serving_size": "1 cup", "gi": "medium", "category": "meal",
                "variations": ["dal khichdi", "moong dal khichdi"]},
    
    # === DESSERTS & SWEETS ===
    "ice cream": {"carbs_per_serving": 25, "serving_size": "1/2 cup", "gi": "high", "category": "dessert",
                  "variations": ["icecream", "gelato", "kulfi", "softy"]},
    "cake": {"carbs_per_serving": 35, "serving_size": "1 slice", "gi": "high", "category": "dessert",
             "variations": ["piece of cake", "birthday cake", "chocolate cake", "pastry"]},
    "cookie": {"carbs_per_serving": 10, "serving_size": "1 cookie", "gi": "high", "category": "dessert",
               "variations": ["cookies", "biscuit", "biscuits", "parle g", "oreo"]},
    "chocolate": {"carbs_per_serving": 15, "serving_size": "1 oz", "gi": "medium", "category": "dessert",
                  "variations": ["chocolate bar", "candy bar", "dairy milk", "kitkat"]},
    "gulab jamun": {"carbs_per_serving": 30, "serving_size": "2 pieces", "gi": "high", "category": "dessert",
                    "variations": ["gulabjamun"]},
    "rasgulla": {"carbs_per_serving": 25, "serving_size": "2 pieces", "gi": "high", "category": "dessert",
                 "variations": ["rasagulla", "rosogolla"]},
    "jalebi": {"carbs_per_serving": 35, "serving_size": "3 pieces", "gi": "high", "category": "dessert",
               "variations": ["imarti"]},
    "ladoo": {"carbs_per_serving": 20, "serving_size": "1 piece", "gi": "high", "category": "dessert",
              "variations": ["laddoo", "laddu", "besan ladoo", "motichoor ladoo", "boondi ladoo"]},
    "barfi": {"carbs_per_serving": 18, "serving_size": "1 piece", "gi": "high", "category": "dessert",
              "variations": ["burfi", "kaju katli", "kaju barfi", "milk barfi"]},
    "halwa": {"carbs_per_serving": 30, "serving_size": "1/2 cup", "gi": "high", "category": "dessert",
              "variations": ["gajar halwa", "sooji halwa", "moong dal halwa", "suji halwa"]},
    "kheer": {"carbs_per_serving": 35, "serving_size": "1 cup", "gi": "high", "category": "dessert",
              "variations": ["rice pudding", "payasam", "phirni"]},
    "mithai": {"carbs_per_serving": 25, "serving_size": "2 pieces", "gi": "high", "category": "dessert",
               "variations": ["indian sweets", "sweets", "meetha"]},
    
    # === SOUTH INDIAN ACCOMPANIMENTS ===
    "sambar": {"carbs_per_serving": 15, "serving_size": "1 cup", "gi": "low", "category": "curry",
               "variations": ["sambhar", "sambar rice"]},
    "chutney": {"carbs_per_serving": 5, "serving_size": "2 tbsp", "gi": "low", "category": "condiment",
                "variations": ["coconut chutney", "tomato chutney", "mint chutney", "green chutney", "pudina chutney"]},
    "rasam": {"carbs_per_serving": 8, "serving_size": "1 cup", "gi": "low", "category": "soup",
              "variations": ["rasam rice", "pepper rasam"]},
    "uttapam": {"carbs_per_serving": 30, "serving_size": "1 piece", "gi": "medium", "category": "grain",
                "variations": ["uthappam", "onion uttapam", "vegetable uttapam"]},
    "pongal": {"carbs_per_serving": 35, "serving_size": "1 cup", "gi": "medium", "category": "grain",
               "variations": ["ven pongal", "khara pongal"]},
    "vada": {"carbs_per_serving": 15, "serving_size": "1 piece", "gi": "medium", "category": "snack",
             "variations": ["medu vada", "urad dal vada", "dahi vada", "sabudana vada"]},
    
    # === SNACKS ===
    "chips": {"carbs_per_serving": 15, "serving_size": "1 oz", "gi": "high", "category": "snack",
              "variations": ["potato chips", "lays", "kurkure", "namkeen", "sev", "mixture"]},
    "popcorn": {"carbs_per_serving": 15, "serving_size": "3 cups", "gi": "medium", "category": "snack",
                "variations": ["pop corn"]},
    "nuts": {"carbs_per_serving": 5, "serving_size": "1 oz", "gi": "low", "category": "snack",
             "variations": ["almonds", "cashews", "peanuts", "walnuts", "badam", "kaju", "mungfali", "dry fruits"]},
    "momos": {"carbs_per_serving": 25, "serving_size": "6 pieces", "gi": "medium", "category": "snack",
              "variations": ["dumplings", "steamed momos", "fried momos"]},
    "maggi": {"carbs_per_serving": 45, "serving_size": "1 pack", "gi": "high", "category": "snack",
              "variations": ["instant noodles", "cup noodles", "ramen"]},
}

# ============================================================================
# COMPREHENSIVE ACTIVITY DATABASE
# ============================================================================
ACTIVITY_DATABASE = {
    # Light activities
    "walk": {"intensity": "light", "calories_per_min": 4, "glucose_impact": -5,
             "variations": ["walking", "stroll", "morning walk", "evening walk"]},
    "yoga": {"intensity": "light", "calories_per_min": 3, "glucose_impact": -3,
             "variations": ["stretching", "meditation", "pranayama", "asana"]},
    "housework": {"intensity": "light", "calories_per_min": 3, "glucose_impact": -3,
                  "variations": ["cleaning", "mopping", "sweeping", "dusting"]},
    
    # Moderate activities
    "jog": {"intensity": "moderate", "calories_per_min": 8, "glucose_impact": -15,
            "variations": ["jogging", "light run", "slow run"]},
    "bike": {"intensity": "moderate", "calories_per_min": 7, "glucose_impact": -12,
             "variations": ["cycling", "bicycle", "biking", "cycle"]},
    "swim": {"intensity": "moderate", "calories_per_min": 8, "glucose_impact": -15,
             "variations": ["swimming", "pool", "laps"]},
    "dance": {"intensity": "moderate", "calories_per_min": 6, "glucose_impact": -10,
              "variations": ["dancing", "zumba", "aerobics"]},
    "tennis": {"intensity": "moderate", "calories_per_min": 7, "glucose_impact": -12,
               "variations": ["badminton", "table tennis", "squash"]},
    "stairs": {"intensity": "moderate", "calories_per_min": 8, "glucose_impact": -12,
               "variations": ["climbing stairs", "stair climbing", "steps"]},
    
    # Vigorous activities
    "run": {"intensity": "vigorous", "calories_per_min": 12, "glucose_impact": -25,
            "variations": ["running", "sprint", "sprinting", "fast run"]},
    "gym": {"intensity": "vigorous", "calories_per_min": 10, "glucose_impact": -20,
            "variations": ["workout", "exercise", "training", "lift", "weights", "weight training", "strength training"]},
    "hiit": {"intensity": "vigorous", "calories_per_min": 14, "glucose_impact": -30,
             "variations": ["high intensity", "interval training", "crossfit", "tabata"]},
    "basketball": {"intensity": "vigorous", "calories_per_min": 10, "glucose_impact": -20,
                   "variations": ["ball game"]},
    "soccer": {"intensity": "vigorous", "calories_per_min": 10, "glucose_impact": -20,
               "variations": ["football", "futsal"]},
    "cricket": {"intensity": "moderate", "calories_per_min": 6, "glucose_impact": -10,
                "variations": ["playing cricket", "batting", "bowling"]},
}

# Quantity words mapping
QUANTITY_WORDS = {
    "zero": 0, "no": 0, "none": 0,
    "a": 1, "an": 1, "one": 1, "single": 1,
    "couple": 2, "two": 2, "pair": 2,
    "few": 3, "three": 3,
    "four": 4, "several": 4,
    "five": 5, "six": 6, "half dozen": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "dozen": 12,
    "half": 0.5, "quarter": 0.25,
    "small": 0.7, "medium": 1, "large": 1.5, "extra large": 2, "huge": 2,
    "little": 0.5, "bit": 0.5, "some": 1, "lot": 2, "lots": 2, "plenty": 2
}

# Time keywords
TIME_KEYWORDS = {
    "breakfast": {"time": 8, "meal_type": "breakfast"},
    "lunch": {"time": 13, "meal_type": "lunch"},
    "dinner": {"time": 20, "meal_type": "dinner"},
    "snack": {"time": None, "meal_type": "snack"},
    "morning": {"time": 9, "meal_type": "morning"},
    "afternoon": {"time": 14, "meal_type": "afternoon"},
    "evening": {"time": 18, "meal_type": "evening"},
    "night": {"time": 21, "meal_type": "night"},
    "now": {"time": None, "meal_type": "current"},
    "just": {"time": None, "meal_type": "current"},
}


class EnhancedNLPProcessor:
    """Advanced NLP Processor for health management"""
    
    def __init__(self):
        self.food_db = FOOD_CARB_DATABASE
        self.activity_db = ACTIVITY_DATABASE
        self.quantity_words = QUANTITY_WORDS
        self.time_keywords = TIME_KEYWORDS
        
        self.food_variations = {}
        self.activity_variations = {}
        self._sorted_food_keys = []
        self._sorted_activity_keys = []
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
        
        self._sorted_food_keys = sorted(self.food_variations.keys(), key=len, reverse=True)
        self._sorted_activity_keys = sorted(self.activity_variations.keys(), key=len, reverse=True)

    def parse_user_text(self, text: str) -> Dict:
        lower_text = text.lower().strip()
        
        entities = {
            "carbs": 0, "foods_detected": [], "activities_detected": [],
            "timing": None, "meal_type": None, "confidence": 0.0,
            "original_text": text, "warnings": [],
            "intent": self._detect_intent(lower_text),
            "gi_impact": "unknown", "health_tips": []
        }
        
        entities.update(self._extract_timing(lower_text))
        
        food_results, remaining_text = self._extract_foods_with_quantities(lower_text)
        entities["carbs"] = food_results["total_carbs"]
        entities["foods_detected"] = food_results["foods"]
        entities["gi_impact"] = food_results.get("overall_gi", "unknown")
        
        explicit_carbs = self._extract_explicit_carbs(lower_text)
        if explicit_carbs > 0:
            entities["carbs"] = explicit_carbs
            entities["warnings"].append("Used explicit carb amount")
        
        entities["activities_detected"] = self._extract_activities(remaining_text)
        entities["confidence"] = self._calculate_confidence(entities, lower_text)
        entities["health_tips"] = self._generate_health_tips(entities)
        
        return entities

    def _detect_intent(self, text: str) -> str:
        greetings = ['hi', 'hello', 'hey', 'howdy', 'good morning', 'good evening']
        if any(g in text for g in greetings):
            return "greeting"
        
        status_patterns = ['how am i', "how's my", 'my status', 'my glucose', 'my sugar',
                          'blood sugar', 'current level', "what's my", 'check my']
        if any(p in text for p in status_patterns):
            return "status_check"
        
        food_patterns = ['i ate', 'i had', "i'm eating", 'just ate', 'eating', 
                        'for breakfast', 'for lunch', 'for dinner', 'having']
        if any(p in text for p in food_patterns):
            return "food_log"
        
        exercise_patterns = ['went for', 'did some', 'just finished', 'worked out',
                           'exercised', 'played', 'running', 'walking', 'gym']
        if any(p in text for p in exercise_patterns):
            return "activity_log"
        
        question_patterns = ['what should', 'should i', 'can i', 'recommend', 
                           'suggest', 'advice', 'help', 'how much']
        if any(p in text for p in question_patterns):
            return "question"
        
        return "general"

    def _extract_foods_with_quantities(self, text: str) -> Tuple[Dict, str]:
        foods_found = []
        total_carbs = 0
        gi_scores = []
        text_copy = " " + text + " "

        for pattern in self._sorted_food_keys:
            pattern_regex = r'\b' + re.escape(pattern) + r's?\b'
            
            for match in re.finditer(pattern_regex, text_copy, re.IGNORECASE):
                start_pos = match.start()
                if text_copy[start_pos:start_pos+1] == '#':
                    continue

                main_food_key = self.food_variations[pattern]
                food_data = self.food_db[main_food_key]
                
                quantity = self._find_quantity_near_food(text_copy, start_pos)
                carbs = round(food_data["carbs_per_serving"] * quantity, 1)
                
                foods_found.append({
                    "food": main_food_key, "quantity": quantity, "carbs": carbs,
                    "serving_size": food_data["serving_size"],
                    "gi": food_data.get("gi", "medium"),
                    "category": food_data.get("category", "other")
                })
                
                total_carbs += carbs
                gi_scores.append(food_data.get("gi", "medium"))
                text_copy = text_copy[:start_pos] + "#" * len(match.group()) + text_copy[match.end():]
        
        overall_gi = "low"
        if gi_scores:
            if "high" in gi_scores:
                overall_gi = "high" if gi_scores.count("high") > len(gi_scores) / 2 else "medium"
            elif "medium" in gi_scores:
                overall_gi = "medium"
        
        return {"foods": foods_found, "total_carbs": round(total_carbs, 1), "overall_gi": overall_gi}, text_copy

    def _find_quantity_near_food(self, text: str, food_pos: int) -> float:
        window_text = text[max(0, food_pos - 25):food_pos].lower()
        
        number_match = re.search(r'(\d+(?:\.\d+)?)\s*$', window_text)
        if number_match:
            try:
                return float(number_match.group(1))
            except:
                pass
        
        for word, value in sorted(self.quantity_words.items(), key=lambda x: len(x[0]), reverse=True):
            if re.search(r'\b' + re.escape(word) + r'\b', window_text):
                return value
        
        return 1.0

    def _extract_explicit_carbs(self, text: str) -> int:
        patterns = [
            r'(\d+)\s*(?:g|grams?)\s*(?:of\s*)?carbs?',
            r'(\d+)\s*carbs?',
            r'carbs?\s*[:=]?\s*(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        return 0

    def _extract_activities(self, text: str) -> List[Dict]:
        activities = []
        text_lower = text.lower()
        
        for pattern in self._sorted_activity_keys:
            if pattern in text_lower:
                main_activity_key = self.activity_variations[pattern]
                if any(a["activity"] == main_activity_key for a in activities):
                    continue
                    
                activity_data = self.activity_db[main_activity_key]
                duration = self._extract_duration_near_activity(text_lower, pattern)
                
                activities.append({
                    "activity": main_activity_key,
                    "intensity": activity_data["intensity"],
                    "duration_minutes": duration,
                    "calories_estimate": round(duration * activity_data["calories_per_min"]),
                    "glucose_impact": activity_data["glucose_impact"]
                })
        
        return activities

    def _extract_duration_near_activity(self, text: str, activity_pattern: str) -> int:
        activity_pos = text.find(activity_pattern)
        if activity_pos == -1:
            return 30
        
        window_start = max(0, activity_pos - 30)
        window_end = min(len(text), activity_pos + len(activity_pattern) + 30)
        window_text = text[window_start:window_end]
        
        duration_patterns = [
            r'(\d+)\s*(?:minutes?|mins?|min)',
            r'(\d+)\s*(?:hours?|hrs?|hr)',
            r'for\s*(\d+)',
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, window_text)
            if match:
                value = int(match.group(1))
                if 'hour' in pattern or 'hr' in pattern:
                    return value * 60
                return min(value, 300)
        
        return 30

    def _extract_timing(self, text: str) -> Dict:
        timing_info = {"timing": None, "meal_type": None}
        for keyword, data in self.time_keywords.items():
            if keyword in text:
                timing_info["timing"] = data["time"]
                timing_info["meal_type"] = data["meal_type"]
                break
        return timing_info

    def _calculate_confidence(self, entities: Dict, text: str) -> float:
        confidence = 0.0
        if entities["foods_detected"]: confidence += 0.35
        if entities["carbs"] > 0: confidence += 0.25
        if entities["activities_detected"]: confidence += 0.2
        if entities["meal_type"]: confidence += 0.1
        if entities["intent"] != "general": confidence += 0.1
        if len(text.split()) < 3: confidence *= 0.85
        return min(confidence, 1.0)

    def _generate_health_tips(self, entities: Dict) -> List[str]:
        tips = []
        
        if entities.get("gi_impact") == "high":
            tips.append("High GI foods - consider pairing with protein/fiber to slow glucose spike")
        
        carbs = entities.get("carbs", 0)
        if carbs > 60:
            tips.append("High carb meal - consider a short walk after eating")
        elif 0 < carbs < 15:
            tips.append("Low carb intake - minimal blood sugar impact expected")
        
        for activity in entities.get("activities_detected", []):
            if activity["intensity"] == "vigorous":
                tips.append("Vigorous exercise may cause glucose drop - have a snack ready")
        
        meal_type = entities.get("meal_type")
        if meal_type == "breakfast":
            tips.append("Morning insulin resistance is common - monitor after breakfast")
        elif meal_type in ["evening", "night"]:
            tips.append("Late meals may affect overnight glucose")
        
        return tips[:3]

    def get_insulin_adjustment_suggestion(self, entities: Dict) -> Dict:
        suggestions = {
            "carb_bolus_needed": False, "exercise_reduction": False,
            "timing_considerations": [], "estimated_carb_bolus": 0,
            "exercise_reduction_percent": 0, "reasoning": ""
        }
        
        carbs = entities.get("carbs", 0)
        if carbs > 5:
            suggestions["carb_bolus_needed"] = True
            suggestions["estimated_carb_bolus"] = round(carbs / 12, 1)
            suggestions["reasoning"] = f"Calculated for {carbs}g carbs"
        
        if entities.get("activities_detected"):
            for activity in entities["activities_detected"]:
                if activity["intensity"] == "vigorous":
                    suggestions["exercise_reduction"] = True
                    suggestions["exercise_reduction_percent"] = 30
                elif activity["intensity"] == "moderate":
                    suggestions["exercise_reduction"] = True
                    suggestions["exercise_reduction_percent"] = 20
        
        if entities.get("gi_impact") == "high":
            suggestions["timing_considerations"].append("High GI meal - consider pre-bolusing 15-20 min before")
        
        return suggestions

    def get_food_suggestions(self, current_glucose: float, time_of_day: str | None = None) -> List[Dict]:
        suggestions = []
        
        if current_glucose < 70:
            suggestions = [
                {"food": "orange juice", "reason": "Fast glucose boost", "carbs": 25},
                {"food": "banana", "reason": "Quick energy", "carbs": 27},
                {"food": "glucose tablets", "reason": "Precise 15g portions", "carbs": 15}
            ]
        elif current_glucose > 180:
            suggestions = [
                {"food": "salad", "reason": "Very low carb", "carbs": 5},
                {"food": "eggs", "reason": "Protein-rich, low carb", "carbs": 1},
                {"food": "paneer", "reason": "Low carb protein", "carbs": 3},
                {"food": "chicken", "reason": "Zero carbs", "carbs": 0}
            ]
        else:
            if time_of_day == "breakfast":
                suggestions = [
                    {"food": "oatmeal", "reason": "Low GI, sustained energy", "carbs": 27},
                    {"food": "idli", "reason": "Light, easy to digest", "carbs": 12},
                    {"food": "eggs", "reason": "Protein-rich start", "carbs": 1}
                ]
            elif time_of_day == "lunch":
                suggestions = [
                    {"food": "dal", "reason": "Protein + fiber", "carbs": 20},
                    {"food": "roti", "reason": "Better than rice for glucose", "carbs": 18},
                    {"food": "salad", "reason": "Add fiber", "carbs": 5}
                ]
            else:
                suggestions = [
                    {"food": "nuts", "reason": "Healthy fats, low carbs", "carbs": 5},
                    {"food": "guava", "reason": "Low GI fruit", "carbs": 8},
                    {"food": "paneer", "reason": "Protein snack", "carbs": 3}
                ]
        
        return suggestions

    def get_activity_suggestions(self, current_glucose: float) -> List[Dict]:
        """Get activity suggestions based on current glucose"""
        suggestions = []
        
        if current_glucose > 180:
            suggestions = [
                {"activity": "walk", "duration": 20, "reason": "Gentle way to lower glucose"},
                {"activity": "yoga", "duration": 15, "reason": "Reduces stress and glucose"},
                {"activity": "stairs", "duration": 10, "reason": "Quick glucose reduction"}
            ]
        elif current_glucose < 100:
            suggestions = [
                {"activity": "yoga", "duration": 20, "reason": "Gentle, won't drop glucose much"},
                {"activity": "walk", "duration": 15, "reason": "Light activity, have snack ready"}
            ]
        else:
            suggestions = [
                {"activity": "walk", "duration": 30, "reason": "Great for overall health"},
                {"activity": "jog", "duration": 20, "reason": "Moderate cardio"},
                {"activity": "gym", "duration": 30, "reason": "Build muscle, improve sensitivity"}
            ]
        
        return suggestions


# Global instance
nlp_processor = EnhancedNLPProcessor()

def parse_text(text: str) -> Dict:
    return nlp_processor.parse_user_text(text)

def get_suggestions(entities: Dict) -> Dict:
    return nlp_processor.get_insulin_adjustment_suggestion(entities)
