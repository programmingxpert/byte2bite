import json
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent

# Load recipe dataset using absolute path
with open(SCRIPT_DIR / "recipes.json", "r", encoding="utf-8") as f:
    RECIPES = json.load(f)


def find_best_recipes(user_ingredients, top_n=20, dietary_preference=None, min_match=0.3, sort_by="match_percentage"):
    """
    Find best matching recipes with improved scoring algorithm using fuzzy ingredient matching.
    Supports both simple ingredient lists and quantity-aware ingredient objects.
    
    Args:
        user_ingredients: List of available ingredients (strings or dicts with 'name' and 'count')
        top_n: Maximum number of recipes to return (default: 20)
        dietary_preference: Filter by dietary preference (vegetarian/non-vegetarian/all)
        min_match: Minimum match percentage to include recipe (default: 0.3 = 30%)
        sort_by: Sorting strategy - "match_percentage" (default) or "ingredients_used"
    
    Returns:
        List of recipe matches sorted by specified strategy
        - "match_percentage": Sort by (score, utilization, ingredients_used) - prioritizes completeness
        - "ingredients_used": Sort by (ingredients_used, utilization, score) - prioritizes ingredient usage
    """
    results = []
    
    # Normalize user ingredients - handle both formats (backward compatibility)
    user_ingredients_normalized = []
    user_ingredients_with_counts = {}
    
    for item in user_ingredients:
        if isinstance(item, dict):
            # New format: {"name": "apple", "count": 3}
            name = item.get("name", "").lower().strip()
            count = item.get("count", 1)
            user_ingredients_normalized.append(name)
            user_ingredients_with_counts[name] = count
        else:
            # Old format: simple string
            name = item.lower().strip()
            user_ingredients_normalized.append(name)
            user_ingredients_with_counts[name] = 1

    # Filter recipes by dietary preference if specified
    filtered_recipes = RECIPES
    if dietary_preference and dietary_preference.lower() != "all":
        filtered_recipes = [r for r in RECIPES if r.get("dietary") == dietary_preference.lower()]

    for recipe in filtered_recipes:
        # Normalize recipe ingredients to lowercase and strip whitespace
        recipe_ingredients_normalized = [x.lower().strip() for x in recipe["ingredients"]]
        
        if len(recipe_ingredients_normalized) == 0:
            continue

        # Use improved fuzzy matching with stricter rules to prevent false positives
        matched_ingredients = []
        matched_user_ingredients = set()
        quantity_info = {}  # Track quantity sufficiency for each matched ingredient
        
        for recipe_ing in recipe_ingredients_normalized:
            for user_ing in user_ingredients_normalized:
                # Stricter matching rules to prevent false positives like "water" matching "watermelon"
                # Rule 1: Exact match (highest priority)
                if user_ing == recipe_ing:
                    matched_ingredients.append(recipe_ing)
                    matched_user_ingredients.add(user_ing)
                    
                    # Track quantity information
                    user_count = user_ingredients_with_counts.get(user_ing, 1)
                    quantity_info[recipe_ing] = {
                        "user_has": user_count,
                        "sufficient": True  # Assume sufficient unless we have recipe quantity requirements
                    }
                    break  # Found a match for this recipe ingredient
                
                # Rule 2: Multi-word recipe ingredient contains user ingredient as a complete word
                # e.g., "cheddar cheese" contains "cheese" as a word ✓
                # but "watermelon" does NOT contain "water" as a word ✗
                elif len(user_ing) >= 4 and user_ing in recipe_ing and recipe_ing != user_ing:
                    # Split both into words and check for exact word match
                    words_in_recipe = recipe_ing.split()
                    # Only match if user ingredient is an exact word in the recipe ingredient
                    if user_ing in words_in_recipe:
                        matched_ingredients.append(recipe_ing)
                        matched_user_ingredients.add(user_ing)
                        
                        # Track quantity information
                        user_count = user_ingredients_with_counts.get(user_ing, 1)
                        quantity_info[recipe_ing] = {
                            "user_has": user_count,
                            "sufficient": True
                        }
                        break
                
                # Rule 3: Multi-word user ingredient contains recipe ingredient as a complete word
                # e.g., user has "cheddar cheese", recipe needs "cheese" ✓
                elif len(recipe_ing) >= 4 and recipe_ing in user_ing and recipe_ing != user_ing:
                    # Split both into words and check for exact word match
                    words_in_user = user_ing.split()
                    # Only match if recipe ingredient is an exact word in the user ingredient
                    if recipe_ing in words_in_user:
                        matched_ingredients.append(recipe_ing)
                        matched_user_ingredients.add(user_ing)
                        
                        # Track quantity information
                        user_count = user_ingredients_with_counts.get(user_ing, 1)
                        quantity_info[recipe_ing] = {
                            "user_has": user_count,
                            "sufficient": True
                        }
                        break
        
        matches_count = len(matched_ingredients)
        
        # Score calculation: percentage of recipe ingredients met
        match_percentage = matches_count / len(recipe_ingredients_normalized)
        
        # Only include recipes with minimum match threshold OR at least 2 matching ingredients
        if match_percentage < min_match and matches_count < 2:
            continue

        # Calculate utilization score: how many user ingredients are used
        utilization_score = len(matched_user_ingredients) / len(user_ingredients_normalized) if len(user_ingredients_normalized) > 0 else 0

        # Get missing ingredients
        missing_ingredients = [ing for ing in recipe_ingredients_normalized if ing not in matched_ingredients]

        results.append({
            "name": recipe["name"],
            "score": round(match_percentage * 100, 2),
            "matched": matched_ingredients,
            "missing": missing_ingredients,
            "target": recipe.get("target", "General"),
            "dietary": recipe.get("dietary", "vegetarian"),
            "ingredients_used": len(matched_user_ingredients),  # Number of unique user ingredients used
            "utilization": round(utilization_score * 100, 2),  # Percentage of user ingredients utilized
            "quantity_info": quantity_info,  # Quantity sufficiency information
            "cuisine": recipe.get("cuisine", "Unknown"),
            "difficulty": recipe.get("difficulty", "Medium"),
            "time": recipe.get("time", "30 minutes"),
            "servings": recipe.get("servings", 2),
            "description": recipe.get("description", "")
        })

    # Apply sorting strategy based on sort_by parameter
    if sort_by == "ingredients_used":
        # Sort by: (1) Number of user ingredients used (DESC), (2) Utilization score (DESC), (3) Match percentage (DESC)
        # This prioritizes recipes that use MORE of your available ingredients
        results.sort(key=lambda x: (x["ingredients_used"], x["utilization"], x["score"]), reverse=True)
    else:
        # Default: Sort by: (1) Match percentage (DESC), (2) Utilization score (DESC), (3) Number of user ingredients used (DESC)
        # This prioritizes recipes with HIGHER match percentage (completeness)
        results.sort(key=lambda x: (x["score"], x["utilization"], x["ingredients_used"]), reverse=True)

    return results[:top_n]

# Made with Bob
