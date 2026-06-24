"""
Recommendation Engine Module
Handles missing ingredient detection, substitutions, and recipe prioritization
"""

from typing import List, Dict, Tuple, Optional, Any
import json


# Common ingredient substitutions
SUBSTITUTIONS = {
    "curd": ["yogurt", "buttermilk", "sour cream"],
    "yogurt": ["curd", "buttermilk", "sour cream"],
    "besan": ["chickpea flour", "gram flour"],
    "atta": ["whole wheat flour", "wheat flour"],
    "sooji": ["semolina", "rava"],
    "capsicum": ["bell pepper", "sweet pepper"],
    "dal": ["lentils", "pulses"],
    "roti": ["chapati", "flatbread"],
    "bread": ["toast", "pav"],
    "peanut": ["groundnut", "cashew", "almond"],
    "tomato": ["tomato puree", "canned tomato"],
    "lemon": ["lime", "vinegar"],
    "milk": ["almond milk", "soy milk", "coconut milk"],
    "potato": ["sweet potato", "yam"],
    "onion": ["shallot", "spring onion"],
    "carrot": ["beetroot", "radish"],
    "cabbage": ["lettuce", "kale"]
}


# Ingredient categories for smart grouping
INGREDIENT_CATEGORIES = {
    "grains": ["rice", "atta", "bread", "roti", "sooji"],
    "dairy": ["curd", "milk", "yogurt", "buttermilk"],
    "vegetables": ["tomato", "onion", "potato", "carrot", "capsicum", "cabbage"],
    "legumes": ["dal", "besan", "lentils"],
    "citrus": ["lemon", "lime"],
    "nuts": ["peanut", "cashew", "almond"],
    "scraps": ["vegetable peel"]
}


def detect_missing_ingredients(
    user_ingredients: List[str],
    recipe_ingredients: List[str]
) -> List[str]:
    """
    Detect which ingredients are missing for a recipe
    
    Args:
        user_ingredients: Ingredients user has
        recipe_ingredients: Ingredients needed for recipe
        
    Returns:
        List of missing ingredients
    """
    user_set = set(ing.lower() for ing in user_ingredients)
    recipe_set = set(ing.lower() for ing in recipe_ingredients)
    
    missing = list(recipe_set - user_set)
    return missing


def suggest_substitutions(
    missing_ingredients: List[str],
    user_ingredients: List[str]
) -> Dict[str, List[str]]:
    """
    Suggest substitutions for missing ingredients based on what user has
    
    Args:
        missing_ingredients: Ingredients that are missing
        user_ingredients: Ingredients user has available
        
    Returns:
        Dictionary mapping missing ingredient to possible substitutes
    """
    suggestions = {}
    user_set = set(ing.lower() for ing in user_ingredients)
    
    for missing in missing_ingredients:
        missing_lower = missing.lower()
        
        # Check if we have substitution data for this ingredient
        if missing_lower in SUBSTITUTIONS:
            possible_subs = SUBSTITUTIONS[missing_lower]
            
            # Find which substitutes the user actually has
            available_subs = [sub for sub in possible_subs if sub in user_set]
            
            if available_subs:
                suggestions[missing] = available_subs
    
    return suggestions


def get_ingredient_category(ingredient: str) -> Optional[str]:
    """
    Get the category of an ingredient
    
    Args:
        ingredient: Ingredient name
        
    Returns:
        Category name or None
    """
    ingredient_lower = ingredient.lower()
    
    for category, items in INGREDIENT_CATEGORIES.items():
        if ingredient_lower in items:
            return category
    
    return None


def calculate_recipe_priority(
    recipe: Dict[str, Any],
    user_ingredients: List[str],
    prioritize_waste_reduction: bool = True
) -> float:
    """
    Calculate priority score for a recipe based on multiple factors
    
    Args:
        recipe: Recipe dictionary with matched, missing, target, score
        user_ingredients: User's available ingredients
        prioritize_waste_reduction: Whether to prioritize waste reduction recipes
        
    Returns:
        Priority score (higher is better)
    """
    # Base score from match percentage
    base_score = recipe.get("score", 0)
    
    # Factor 1: Match percentage (40% weight)
    match_component = base_score * 0.4
    
    # Factor 2: Number of ingredients used (30% weight)
    matched_count = len(recipe.get("matched", []))
    ingredient_component = min(matched_count / 5, 1.0) * 30
    
    # Factor 3: Waste reduction target (30% weight)
    target = recipe.get("target", "General")
    if prioritize_waste_reduction and target.lower() != "general":
        waste_component = 30
    else:
        waste_component = 15
    
    # Factor 4: Penalty for many missing ingredients
    missing_count = len(recipe.get("missing", []))
    missing_penalty = min(missing_count * 2, 10)
    
    total_score = match_component + ingredient_component + waste_component - missing_penalty
    
    return round(max(total_score, 0), 2)


def rank_recipes(
    recipes: List[Dict[str, Any]],
    user_ingredients: List[str],
    prioritize_waste_reduction: bool = True
) -> List[Dict[str, Any]]:
    """
    Rank recipes by priority score
    
    Args:
        recipes: List of recipe dictionaries
        user_ingredients: User's available ingredients
        prioritize_waste_reduction: Whether to prioritize waste reduction
        
    Returns:
        Sorted list of recipes with priority scores
    """
    ranked = []
    
    for recipe in recipes:
        priority = calculate_recipe_priority(recipe, user_ingredients, prioritize_waste_reduction)
        recipe_copy = recipe.copy()
        recipe_copy["priority_score"] = priority
        ranked.append(recipe_copy)
    
    # Sort by priority score (descending)
    ranked.sort(key=lambda x: x["priority_score"], reverse=True)
    
    return ranked


def get_top_recommendation(
    recipes: List[Dict[str, Any]],
    user_ingredients: List[str]
) -> Optional[Dict[str, Any]]:
    """
    Get the single best recipe recommendation
    
    Args:
        recipes: List of recipe matches
        user_ingredients: User's available ingredients
        
    Returns:
        Best recipe with additional recommendation data
    """
    if not recipes:
        return None
    
    # Rank all recipes
    ranked = rank_recipes(recipes, user_ingredients, prioritize_waste_reduction=True)
    
    # Get top recipe
    top_recipe = ranked[0]
    
    # Add substitution suggestions for missing ingredients
    missing = top_recipe.get("missing", [])
    substitutions = suggest_substitutions(missing, user_ingredients)
    
    # Enhance with recommendation data
    recommendation = top_recipe.copy()
    recommendation["substitutions"] = substitutions
    recommendation["recommendation_reason"] = generate_recommendation_reason(top_recipe, user_ingredients)
    
    return recommendation


def generate_recommendation_reason(
    recipe: Dict[str, Any],
    user_ingredients: List[str]
) -> str:
    """
    Generate human-readable reason for recommending this recipe
    
    Args:
        recipe: Recipe dictionary
        user_ingredients: User's available ingredients
        
    Returns:
        Explanation string
    """
    matched_count = len(recipe.get("matched", []))
    missing_count = len(recipe.get("missing", []))
    target = recipe.get("target", "General")
    score = recipe.get("score", 0)
    
    reasons = []
    
    # High match percentage
    if score >= 80:
        reasons.append(f"excellent ingredient match ({score}%)")
    elif score >= 60:
        reasons.append(f"good ingredient match ({score}%)")
    
    # Uses many ingredients
    if matched_count >= 3:
        reasons.append(f"uses {matched_count} of your ingredients")
    
    # Targets waste reduction
    if target.lower() != "general":
        reasons.append(f"specifically designed for {target}")
    
    # Few missing ingredients
    if missing_count == 0:
        reasons.append("requires no additional ingredients")
    elif missing_count == 1:
        reasons.append("only needs 1 additional ingredient")
    
    if not reasons:
        reasons.append("best available match for your ingredients")
    
    return "Recommended because it has " + ", ".join(reasons)


def analyze_ingredient_coverage(
    recipes: List[Dict[str, Any]],
    user_ingredients: List[str]
) -> Dict[str, Any]:
    """
    Analyze how well the recipe set covers user's ingredients
    
    Args:
        recipes: List of recipe matches
        user_ingredients: User's available ingredients
        
    Returns:
        Coverage analysis dictionary
    """
    if not recipes:
        return {
            "total_ingredients": len(user_ingredients),
            "covered_ingredients": 0,
            "uncovered_ingredients": user_ingredients,
            "coverage_percentage": 0.0
        }
    
    # Collect all matched ingredients across all recipes
    all_matched = set()
    for recipe in recipes:
        matched = recipe.get("matched", [])
        all_matched.update(ing.lower() for ing in matched)
    
    user_set = set(ing.lower() for ing in user_ingredients)
    uncovered = list(user_set - all_matched)
    
    coverage_pct = (len(all_matched) / len(user_set) * 100) if user_set else 0
    
    return {
        "total_ingredients": len(user_ingredients),
        "covered_ingredients": len(all_matched),
        "uncovered_ingredients": uncovered,
        "coverage_percentage": round(coverage_pct, 2)
    }


def generate_shopping_list(
    recommended_recipe: Dict[str, Any],
    user_ingredients: List[str]
) -> List[Dict[str, str]]:
    """
    Generate a shopping list for missing ingredients with substitution info
    
    Args:
        recommended_recipe: The recommended recipe
        user_ingredients: User's available ingredients
        
    Returns:
        List of items to buy with substitution suggestions
    """
    missing = recommended_recipe.get("missing", [])
    substitutions = recommended_recipe.get("substitutions", {})
    
    shopping_list = []
    
    for ingredient in missing:
        item = {
            "ingredient": ingredient,
            "category": get_ingredient_category(ingredient) or "other"
        }
        
        # Add substitution info if available
        if ingredient in substitutions:
            item["substitutes"] = substitutions[ingredient]
            item["note"] = f"Can substitute with: {', '.join(substitutions[ingredient])}"
        else:
            item["note"] = "No substitutes available"
        
        shopping_list.append(item)
    
    return shopping_list


def get_recipe_recommendations_with_analysis(
    recipes: List[Dict[str, Any]],
    user_ingredients: List[str]
) -> Dict[str, Any]:
    """
    Get comprehensive recipe recommendations with full analysis
    
    Args:
        recipes: List of recipe matches from recipe_matcher
        user_ingredients: User's available ingredients
        
    Returns:
        Complete recommendation package
    """
    # Get top recommendation
    top_recipe = get_top_recommendation(recipes, user_ingredients)
    
    # Rank all recipes
    ranked_recipes = rank_recipes(recipes, user_ingredients)
    
    # Analyze coverage
    coverage = analyze_ingredient_coverage(recipes, user_ingredients)
    
    # Generate shopping list if there's a recommendation
    shopping_list = []
    if top_recipe:
        shopping_list = generate_shopping_list(top_recipe, user_ingredients)
    
    return {
        "top_recommendation": top_recipe,
        "all_recipes_ranked": ranked_recipes[:10],  # Top 10
        "ingredient_coverage": coverage,
        "shopping_list": shopping_list,
        "total_recipes_analyzed": len(recipes)
    }


if __name__ == "__main__":
    # Test the recommendation engine
    test_ingredients = ["rice", "lemon", "curd", "tomato", "onion"]
    
    test_recipes = [
        {
            "name": "Classic Lemon Rice",
            "score": 100.0,
            "matched": ["rice", "lemon"],
            "missing": [],
            "target": "leftover rice"
        },
        {
            "name": "Curd Rice",
            "score": 100.0,
            "matched": ["rice", "curd"],
            "missing": [],
            "target": "leftover rice"
        },
        {
            "name": "Spicy Roti Upma",
            "score": 66.67,
            "matched": ["onion", "tomato"],
            "missing": ["roti"],
            "target": "leftover roti"
        }
    ]
    
    recommendations = get_recipe_recommendations_with_analysis(test_recipes, test_ingredients)
    
    print("=== Recommendation Analysis ===")
    print(f"Top Recommendation: {recommendations['top_recommendation']['name']}")
    print(f"Priority Score: {recommendations['top_recommendation']['priority_score']}")
    print(f"Reason: {recommendations['top_recommendation']['recommendation_reason']}")
    print(f"\nIngredient Coverage: {recommendations['ingredient_coverage']['coverage_percentage']}%")
    print(f"Shopping List Items: {len(recommendations['shopping_list'])}")

# Made with Bob
