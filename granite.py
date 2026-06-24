"""
Granite AI Module - Local IBM Granite Integration via Ollama
Generates recipe explanations, sustainability analysis, and SDG impact assessments
"""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
import requests

# Import config settings
try:
    from backend.config import MODEL_MODE, TUNNEL_LOCAL_PORT, CLOUD_GRANITE_MODEL, LOCAL_GRANITE_MODEL
except ImportError:
    from config import MODEL_MODE, TUNNEL_LOCAL_PORT, CLOUD_GRANITE_MODEL, LOCAL_GRANITE_MODEL

# Get project root for cache file (use /tmp on Vercel since filesystem is read-only)
SCRIPT_DIR = Path(__file__).parent
if os.getenv("VERCEL"):
    GRANITE_CACHE_FILE = Path("/tmp/granite_cache.json")
else:
    GRANITE_CACHE_FILE = SCRIPT_DIR / "granite_cache.json"

# Ollama API configuration based on mode
if MODEL_MODE in ["cloud", "cloud_direct"]:
    OLLAMA_BASE_URL = f"http://localhost:{TUNNEL_LOCAL_PORT}" if MODEL_MODE == "cloud" else "http://localhost:11434"
    GRANITE_MODEL = CLOUD_GRANITE_MODEL
else:
    OLLAMA_BASE_URL = "http://localhost:11434"
    GRANITE_MODEL = LOCAL_GRANITE_MODEL

import json

def load_cache() -> Dict:
    if GRANITE_CACHE_FILE.exists():
        try:
            with open(GRANITE_CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache_data: Dict):
    try:
        with open(GRANITE_CACHE_FILE, "w") as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        print(f"[Cache Error] Failed to write Granite cache: {e}")


def check_ollama_connection() -> bool:
    """
    Check if Ollama service is running and accessible
    
    Returns:
        True if Ollama is accessible, False otherwise
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def check_model_available(model_name: str = GRANITE_MODEL) -> bool:
    """
    Check if the specified model is available in Ollama
    
    Args:
        model_name: Name of the model to check
        
    Returns:
        True if model is available, False otherwise
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model.get("name", "") for model in data.get("models", [])]
            return any(model_name in model for model in models)
        return False
    except Exception:
        return False


def generate_with_granite(
    prompt: str,
    model: str = GRANITE_MODEL,
    temperature: float = 0.2,
    max_tokens: int = 500
) -> Optional[str]:
    """
    Generate text using Granite model via Ollama
    
    Args:
        prompt: Input prompt for generation
        model: Model name to use
        temperature: Sampling temperature (0.0-1.0)
        max_tokens: Maximum tokens to generate
        
    Returns:
        Generated text or None if error
    """
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            print(f"Error: Ollama API returned status {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("Error: Request to Ollama timed out")
        return None
    except Exception as e:
        print(f"Error generating with Granite: {str(e)}")
        return None


def get_recommendation(
    ingredients: List[str],
    recipes: List[str],
    top_recipe: Optional[Dict] = None
) -> str:
    """
    Get recipe recommendation with sustainability analysis from Granite
    
    Args:
        ingredients: List of available ingredients
        recipes: List of recipe names
        top_recipe: Optional dictionary with top recipe details
        
    Returns:
        Formatted recommendation text
    """
    # Cache check
    sorted_ing = sorted([i.lower().strip() for i in ingredients])
    sorted_rec = sorted([r.lower().strip() for r in recipes])
    top_recipe_name = top_recipe.get("name", "").lower().strip() if top_recipe else ""
    cache_key = hashlib.md5(f"rec|ing:{','.join(sorted_ing)}|rec:{','.join(sorted_rec)}|top:{top_recipe_name}".encode('utf-8')).hexdigest()
    
    cache = load_cache()
    if cache_key in cache:
        print("[Cache Hit] Granite recommendation loaded from cache.")
        return cache[cache_key]

    # Check if Ollama is available
    if not check_ollama_connection() or not check_model_available():
        return generate_fallback_recommendation(ingredients, recipes, top_recipe)
    
    # Build the prompt
    recipe_list = "\n".join([f"- {recipe}" for recipe in recipes])
    ingredient_list = ", ".join(ingredients)
    
    prompt = f"""You are a sustainable cooking assistant powered by IBM Granite AI.

Available ingredients: {ingredient_list}

Recipe candidates:
{recipe_list}

Task: Choose the best recipe that maximizes ingredient usage and reduces food waste.

Provide your response in this exact format:

Recipe Name: [name]
Reason: [brief explanation of why this is the most sustainable choice]
Missing Ingredients: [comma-separated list or 'None']
Waste Reduction Score: [1-10 rating] - [one sentence justification]
Cooking Instructions: [3-5 numbered steps]

Keep your response concise and focused on sustainability."""

    # Generate response
    response = generate_with_granite(prompt, temperature=0.2, max_tokens=500)
    
    if response:
        cache[cache_key] = response
        save_cache(cache)
        return response
    else:
        return generate_fallback_recommendation(ingredients, recipes, top_recipe)


def generate_sdg_impact_analysis(
    recipe_name: str,
    ingredients_used: List[str],
    waste_reduction_score: float,
    co2_saved: float
) -> str:
    """
    Generate SDG 12 impact analysis using Granite
    
    Args:
        recipe_name: Name of the recipe
        ingredients_used: List of ingredients being used
        waste_reduction_score: Waste reduction score (0-10)
        co2_saved: CO2 saved in kg
        
    Returns:
        SDG impact analysis text
    """
    # Cache check
    sorted_ing = sorted([i.lower().strip() for i in ingredients_used])
    cache_key = hashlib.md5(f"sdg|rec:{recipe_name.lower().strip()}|ing:{','.join(sorted_ing)}|waste:{waste_reduction_score}|co2:{co2_saved}".encode('utf-8')).hexdigest()
    
    cache = load_cache()
    if cache_key in cache:
        print("[Cache Hit] Granite SDG analysis loaded from cache.")
        return cache[cache_key]

    if not check_ollama_connection() or not check_model_available():
        return generate_fallback_sdg_analysis(recipe_name, waste_reduction_score, co2_saved)
    
    prompt = f"""Analyze the sustainability impact of this recipe in relation to UN SDG 12 (Responsible Consumption and Production).

Recipe: {recipe_name}
Ingredients Used: {', '.join(ingredients_used)}
Waste Reduction Score: {waste_reduction_score}/10
CO2 Saved: {co2_saved} kg

Provide a brief analysis (3-4 sentences) covering:
1. How this recipe aligns with SDG 12 targets
2. The environmental impact of reducing food waste
3. The broader sustainability benefits

Keep it concise and actionable."""

    response = generate_with_granite(prompt, temperature=0.3, max_tokens=300)
    
    if response:
        cache[cache_key] = response
        save_cache(cache)
        return response
    else:
        return generate_fallback_sdg_analysis(recipe_name, waste_reduction_score, co2_saved)


def generate_sustainability_tips(
    unused_ingredients: List[str],
    recipe_target: str
) -> str:
    """
    Generate sustainability tips for unused ingredients
    
    Args:
        unused_ingredients: List of ingredients not used in recipe
        recipe_target: Target category of the recipe
        
    Returns:
        Sustainability tips text
    """
    if not unused_ingredients:
        return "Great job! You're using all your available ingredients efficiently."
    
    # Cache check
    sorted_unused = sorted([i.lower().strip() for i in unused_ingredients])
    cache_key = hashlib.md5(f"tips|unused:{','.join(sorted_unused)}|target:{recipe_target.lower().strip()}".encode('utf-8')).hexdigest()
    
    cache = load_cache()
    if cache_key in cache:
        print("[Cache Hit] Granite sustainability tips loaded from cache.")
        return cache[cache_key]

    if not check_ollama_connection() or not check_model_available():
        return generate_fallback_tips(unused_ingredients)
    
    ingredient_list = ", ".join(unused_ingredients)
    
    prompt = f"""Provide 2-3 quick sustainability tips for these unused ingredients: {ingredient_list}

Focus on:
- Storage tips to extend shelf life
- Quick recipe ideas to use them soon
- Creative ways to reduce waste

Keep each tip to one sentence. Be practical and actionable."""

    response = generate_with_granite(prompt, temperature=0.4, max_tokens=200)
    
    if response:
        cache[cache_key] = response
        save_cache(cache)
        return response
    else:
        return generate_fallback_tips(unused_ingredients)


def generate_fallback_recommendation(
    ingredients: List[str],
    recipes: List[str],
    top_recipe: Optional[Dict] = None
) -> str:
    """
    Generate fallback recommendation when Granite is unavailable
    
    Args:
        ingredients: Available ingredients
        recipes: Recipe names
        top_recipe: Top recipe details
        
    Returns:
        Formatted recommendation text
    """
    if top_recipe:
        recipe_name = top_recipe.get("name", recipes[0] if recipes else "Unknown")
        matched = top_recipe.get("matched", [])
        missing = top_recipe.get("missing", [])
        score = top_recipe.get("score", 0)
    else:
        recipe_name = recipes[0] if recipes else "Unknown"
        matched = []
        missing = []
        score = 0
    
    missing_text = ", ".join(missing) if missing else "None"
    waste_score = min(10, int(score / 10) + 5)
    
    return f"""Recipe Name: {recipe_name}
Reason: This recipe maximizes the use of your available ingredients ({len(matched)} ingredients matched) and helps reduce food waste effectively.
Missing Ingredients: {missing_text}
Waste Reduction Score: {waste_score}/10 - Excellent utilization of available ingredients with minimal waste generation.
Cooking Instructions:
1. Prepare all ingredients by washing and chopping as needed
2. Follow standard cooking procedures for {recipe_name}
3. Cook until ingredients are well combined and properly done
4. Serve hot and enjoy your sustainable meal

Note: Granite AI is currently unavailable. This is a basic recommendation based on ingredient matching."""


def generate_fallback_sdg_analysis(
    recipe_name: str,
    waste_reduction_score: float,
    co2_saved: float
) -> str:
    """
    Generate fallback SDG analysis when Granite is unavailable
    
    Args:
        recipe_name: Recipe name
        waste_reduction_score: Waste reduction score
        co2_saved: CO2 saved in kg
        
    Returns:
        SDG analysis text
    """
    impact_level = "high" if waste_reduction_score >= 7 else "moderate" if waste_reduction_score >= 5 else "good"
    
    return f"""This recipe demonstrates {impact_level} alignment with UN SDG 12 (Responsible Consumption and Production). By utilizing available ingredients efficiently, you're contributing to Target 12.3: halving per capita food waste. The estimated {co2_saved} kg CO2 savings represents a meaningful reduction in your environmental footprint. This approach to cooking promotes sustainable consumption patterns and helps build a more circular food system."""


def generate_fallback_tips(unused_ingredients: List[str]) -> str:
    """
    Generate fallback tips when Granite is unavailable
    
    Args:
        unused_ingredients: List of unused ingredients
        
    Returns:
        Tips text
    """
    tips = []
    
    for ingredient in unused_ingredients[:3]:
        if ingredient.lower() in ["tomato", "onion", "capsicum"]:
            tips.append(f"Store {ingredient} in a cool, dry place to extend freshness")
        elif ingredient.lower() in ["curd", "milk"]:
            tips.append(f"Use {ingredient} within 2-3 days or freeze for later use")
        elif ingredient.lower() in ["rice", "bread", "roti"]:
            tips.append(f"Transform leftover {ingredient} into a new dish tomorrow")
        else:
            tips.append(f"Consider using {ingredient} in your next meal to minimize waste")
    
    return "\n".join([f"• {tip}" for tip in tips])


if __name__ == "__main__":
    # Test the Granite integration
    print("Testing Granite AI Integration...")
    print(f"Ollama Connection: {'✓' if check_ollama_connection() else '✗'}")
    print(f"Granite Model Available: {'✓' if check_model_available() else '✗'}")
    
    test_ingredients = ["rice", "lemon", "curd"]
    test_recipes = ["Classic Lemon Rice", "Curd Rice", "Vegetable Rice Cutlets"]
    
    print("\nGenerating recommendation...")
    recommendation = get_recommendation(test_ingredients, test_recipes)
    print("\n" + recommendation)

# Made with Bob
