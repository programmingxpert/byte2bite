"""
Sustainability Engine Module
Calculates waste reduction scores, sustainability metrics, and CO2 impact
"""

from typing import List, Dict, Tuple, Any
import math


# CO2 emission factors (kg CO2 per kg of food waste)
CO2_FACTORS = {
    "rice": 2.7,
    "bread": 1.2,
    "roti": 1.2,
    "atta": 0.9,
    "potato": 0.3,
    "tomato": 1.1,
    "onion": 0.4,
    "carrot": 0.4,
    "capsicum": 1.4,
    "cabbage": 0.4,
    "lemon": 0.9,
    "curd": 1.3,
    "dal": 1.5,
    "besan": 1.0,
    "sooji": 0.9,
    "peanut": 2.5,
    "vegetable peel": 0.3,
    "milk": 1.3,
    "default": 1.0
}

# Average weight per ingredient (kg)
AVERAGE_WEIGHTS = {
    "rice": 0.2,
    "bread": 0.05,
    "roti": 0.04,
    "atta": 0.1,
    "potato": 0.15,
    "tomato": 0.1,
    "onion": 0.1,
    "carrot": 0.08,
    "capsicum": 0.12,
    "cabbage": 0.3,
    "lemon": 0.05,
    "curd": 0.2,
    "dal": 0.15,
    "besan": 0.1,
    "sooji": 0.1,
    "peanut": 0.05,
    "vegetable peel": 0.05,
    "milk": 0.25,
    "default": 0.1
}


def calculate_ingredient_utilization(
    user_ingredients: List[str],
    matched_ingredients: List[str],
    recipe_ingredients: List[str]
) -> float:
    """
    Calculate what percentage of user's ingredients are utilized in the recipe
    
    Args:
        user_ingredients: List of ingredients user has
        matched_ingredients: Ingredients that match the recipe
        recipe_ingredients: All ingredients needed for the recipe
        
    Returns:
        Utilization percentage (0-100)
    """
    if not user_ingredients:
        return 0.0
    
    utilization = (len(matched_ingredients) / len(user_ingredients)) * 100
    return round(utilization, 2)


def calculate_waste_reduction_score(
    matched_ingredients: List[str],
    user_ingredients: List[str],
    recipe_target: str = "General"
) -> Tuple[float, str]:
    """
    Calculate waste reduction score based on ingredient usage and recipe target
    
    Args:
        matched_ingredients: Ingredients that match the recipe
        user_ingredients: All ingredients user has
        recipe_target: Target category (e.g., "leftover rice", "stale bread")
        
    Returns:
        Tuple of (score 0-10, explanation string)
    """
    if not user_ingredients:
        return 0.0, "No ingredients provided"
    
    # Base score from utilization
    utilization_ratio = len(matched_ingredients) / len(user_ingredients)
    base_score = utilization_ratio * 7  # Max 7 points from utilization
    
    # Bonus points for targeting specific waste categories
    target_bonus = 0
    if recipe_target and recipe_target.lower() != "general":
        target_bonus = 2.0
        
    # Bonus for high ingredient count (using more ingredients = less waste)
    count_bonus = min(len(matched_ingredients) / 5, 1.0)  # Max 1 point
    
    total_score = base_score + target_bonus + count_bonus
    total_score = min(total_score, 10.0)  # Cap at 10
    
    # Generate explanation
    if total_score >= 8:
        explanation = "Excellent waste reduction - uses most available ingredients efficiently"
    elif total_score >= 6:
        explanation = "Good waste reduction - utilizes several key ingredients"
    elif total_score >= 4:
        explanation = "Moderate waste reduction - some ingredients will be used"
    else:
        explanation = "Limited waste reduction - only few ingredients utilized"
    
    return round(total_score, 1), explanation


def calculate_sustainability_score(
    matched_ingredients: List[str],
    missing_ingredients: List[str],
    recipe_target: str = "General"
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate overall sustainability score with detailed breakdown
    
    Args:
        matched_ingredients: Ingredients that match the recipe
        missing_ingredients: Ingredients needed but not available
        recipe_target: Target category for the recipe
        
    Returns:
        Tuple of (overall score 0-100, breakdown dictionary)
    """
    # Component 1: Ingredient availability (40 points max)
    total_needed = len(matched_ingredients) + len(missing_ingredients)
    if total_needed == 0:
        availability_score = 0
    else:
        availability_score = (len(matched_ingredients) / total_needed) * 40
    
    # Component 2: Waste targeting (30 points max)
    if recipe_target and recipe_target.lower() != "general":
        waste_target_score = 30
    else:
        waste_target_score = 15
    
    # Component 3: Resource efficiency (30 points max)
    # Fewer missing ingredients = more efficient
    if total_needed == 0:
        efficiency_score = 0
    else:
        efficiency_ratio = 1 - (len(missing_ingredients) / max(total_needed, 1))
        efficiency_score = efficiency_ratio * 30
    
    overall_score = availability_score + waste_target_score + efficiency_score
    
    breakdown = {
        "availability": round(availability_score, 1),
        "waste_targeting": round(waste_target_score, 1),
        "resource_efficiency": round(efficiency_score, 1),
        "overall": round(overall_score, 1)
    }
    
    return round(overall_score, 1), breakdown


def estimate_co2_impact(
    ingredients_used: List[str],
    ingredients_saved: List[str]
) -> Dict[str, float]:
    """
    Estimate CO2 impact of using ingredients vs wasting them
    
    Args:
        ingredients_used: Ingredients being used in recipe
        ingredients_saved: Ingredients saved from waste
        
    Returns:
        Dictionary with CO2 metrics in kg
    """
    # Calculate CO2 that would be emitted if ingredients were wasted
    co2_saved = 0.0
    for ingredient in ingredients_saved:
        ingredient_lower = ingredient.lower()
        co2_factor = CO2_FACTORS.get(ingredient_lower, CO2_FACTORS["default"])
        weight = AVERAGE_WEIGHTS.get(ingredient_lower, AVERAGE_WEIGHTS["default"])
        co2_saved += co2_factor * weight
    
    # Calculate CO2 from using ingredients (cooking emissions, ~20% of waste emissions)
    co2_from_cooking = 0.0
    for ingredient in ingredients_used:
        ingredient_lower = ingredient.lower()
        co2_factor = CO2_FACTORS.get(ingredient_lower, CO2_FACTORS["default"])
        weight = AVERAGE_WEIGHTS.get(ingredient_lower, AVERAGE_WEIGHTS["default"])
        co2_from_cooking += (co2_factor * weight * 0.2)
    
    net_co2_saved = co2_saved - co2_from_cooking
    
    return {
        "co2_saved_from_waste": round(co2_saved, 3),
        "co2_from_cooking": round(co2_from_cooking, 3),
        "net_co2_saved": round(max(net_co2_saved, 0), 3),
        "equivalent_km_driven": round(max(net_co2_saved, 0) / 0.12, 2)  # Average car: 0.12 kg CO2/km
    }


def calculate_sdg_alignment(
    waste_reduction_score: float,
    sustainability_score: float,
    co2_saved: float
) -> Dict[str, Any]:
    """
    Calculate alignment with UN SDG 12 (Responsible Consumption and Production)
    
    Args:
        waste_reduction_score: Score from 0-10
        sustainability_score: Score from 0-100
        co2_saved: Net CO2 saved in kg
        
    Returns:
        Dictionary with SDG alignment metrics
    """
    # Normalize scores to 0-100 scale
    waste_score_normalized = waste_reduction_score * 10
    
    # Calculate overall SDG alignment (weighted average)
    sdg_score = (
        waste_score_normalized * 0.4 +
        sustainability_score * 0.4 +
        min(co2_saved * 20, 100) * 0.2  # CO2 impact (capped at 100)
    )
    
    # Determine impact level
    if sdg_score >= 80:
        impact_level = "High Impact"
        description = "Strongly aligned with SDG 12 - Excellent waste reduction and sustainability"
    elif sdg_score >= 60:
        impact_level = "Medium Impact"
        description = "Good alignment with SDG 12 - Significant waste reduction efforts"
    elif sdg_score >= 40:
        impact_level = "Moderate Impact"
        description = "Moderate alignment with SDG 12 - Some waste reduction benefits"
    else:
        impact_level = "Low Impact"
        description = "Limited alignment with SDG 12 - Minimal waste reduction"
    
    return {
        "sdg_score": round(sdg_score, 1),
        "impact_level": impact_level,
        "description": description,
        "targets_addressed": [
            "12.3: Halve per capita food waste",
            "12.5: Reduce waste generation",
            "12.8: Promote sustainable lifestyles"
        ]
    }


def generate_full_sustainability_report(
    user_ingredients: List[str],
    recipe_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate comprehensive sustainability report for a recipe match
    
    Args:
        user_ingredients: List of ingredients user has
        recipe_data: Dictionary with recipe details (matched, missing, target, etc.)
        
    Returns:
        Complete sustainability report dictionary
    """
    matched = recipe_data.get("matched", [])
    missing = recipe_data.get("missing", [])
    target = recipe_data.get("target", "General")
    
    # Calculate all metrics
    utilization = calculate_ingredient_utilization(user_ingredients, matched, matched + missing)
    waste_score, waste_explanation = calculate_waste_reduction_score(matched, user_ingredients, target)
    sustainability_score, sustainability_breakdown = calculate_sustainability_score(matched, missing, target)
    co2_impact = estimate_co2_impact(matched, matched)
    sdg_alignment = calculate_sdg_alignment(waste_score, sustainability_score, co2_impact["net_co2_saved"])
    
    return {
        "ingredient_utilization": utilization,
        "waste_reduction": {
            "score": waste_score,
            "explanation": waste_explanation
        },
        "sustainability": {
            "overall_score": sustainability_score,
            "breakdown": sustainability_breakdown
        },
        "co2_impact": co2_impact,
        "sdg_alignment": sdg_alignment,
        "summary": {
            "ingredients_used": len(matched),
            "ingredients_available": len(user_ingredients),
            "ingredients_needed": len(missing),
            "recipe_target": target
        }
    }


if __name__ == "__main__":
    # Test the sustainability engine
    test_ingredients = ["rice", "lemon", "curd", "tomato"]
    test_recipe = {
        "name": "Classic Lemon Rice",
        "matched": ["rice", "lemon"],
        "missing": [],
        "target": "leftover rice"
    }
    
    report = generate_full_sustainability_report(test_ingredients, test_recipe)
    
    print("=== Sustainability Report ===")
    print(f"Ingredient Utilization: {report['ingredient_utilization']}%")
    print(f"Waste Reduction Score: {report['waste_reduction']['score']}/10")
    print(f"Sustainability Score: {report['sustainability']['overall_score']}/100")
    print(f"CO2 Saved: {report['co2_impact']['net_co2_saved']} kg")
    print(f"SDG 12 Alignment: {report['sdg_alignment']['sdg_score']}/100")

# Made with Bob
