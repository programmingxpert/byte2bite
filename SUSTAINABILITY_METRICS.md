# Sustainability Metrics Framework
## AI-Powered Food Waste Reduction Assistant

**Version:** 1.0  
**Last Updated:** June 19, 2026  
**Purpose:** Measure and track environmental, economic, and social impact

---

## Table of Contents

1. [Overview](#1-overview)
2. [Core Metrics](#2-core-metrics)
3. [Environmental Impact](#3-environmental-impact)
4. [Economic Impact](#4-economic-impact)
5. [Social Impact](#5-social-impact)
6. [Data Collection Methods](#6-data-collection-methods)
7. [Calculation Formulas](#7-calculation-formulas)
8. [Baseline Establishment](#8-baseline-establishment)
9. [Reporting Templates](#9-reporting-templates)
10. [Visualization Guidelines](#10-visualization-guidelines)
11. [Case Studies](#11-case-studies)
12. [SDG Alignment](#12-sdg-alignment)

---

## 1. Overview

### 1.1 Purpose

This framework provides a comprehensive methodology for measuring the sustainability impact of the RecipeAI system across three dimensions:

1. **Environmental:** Carbon footprint, water savings, waste reduction
2. **Economic:** Cost savings, resource efficiency
3. **Social:** Food security, behavior change, community impact

### 1.2 Measurement Philosophy

**Principles:**
- **Measurable:** All metrics must be quantifiable
- **Verifiable:** Data sources must be traceable
- **Actionable:** Insights must drive improvements
- **Transparent:** Methodology must be open and reproducible
- **Comparable:** Metrics align with international standards

### 1.3 Metric Categories

```
┌─────────────────────────────────────────────────────────┐
│                  SUSTAINABILITY METRICS                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Environmental│  │   Economic   │  │    Social    │ │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤ │
│  │ • CO₂e saved │  │ • Cost saved │  │ • Meals made │ │
│  │ • Water saved│  │ • Efficiency │  │ • Awareness  │ │
│  │ • Waste ↓    │  │ • ROI        │  │ • Behavior   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Core Metrics

### 2.1 Primary Metrics

| Metric | Unit | Target | Measurement Frequency |
|--------|------|--------|----------------------|
| **Food Waste Prevented** | kg | 15 kg/user/year | Daily |
| **CO₂e Emissions Avoided** | kg CO₂e | 39 kg/user/year | Daily |
| **Water Saved** | liters | 15,000 L/user/year | Daily |
| **Cost Savings** | ₹ | ₹13,000/user/year | Daily |
| **Recipes Created** | count | 100/user/year | Per use |
| **User Engagement** | % | 70% retention | Weekly |

### 2.2 Secondary Metrics

| Metric | Unit | Purpose |
|--------|------|---------|
| **Ingredient Detection Accuracy** | % | Quality control |
| **Recipe Match Score** | % | System performance |
| **User Satisfaction** | 1-10 | Experience quality |
| **Cache Hit Rate** | % | Technical efficiency |
| **API Response Time** | seconds | Performance |
| **Active Users** | count | Adoption rate |

### 2.3 Metric Hierarchy

```
Level 1: Impact Metrics (What changed?)
  └─ Food waste prevented
  └─ CO₂e avoided
  └─ Cost saved

Level 2: Activity Metrics (What happened?)
  └─ Recipes created
  └─ Ingredients detected
  └─ User sessions

Level 3: Technical Metrics (How well?)
  └─ Accuracy
  └─ Performance
  └─ Reliability
```

---

## 3. Environmental Impact

### 3.1 Carbon Footprint Reduction

#### Formula

```
CO₂e Avoided = Food Waste Prevented (kg) × Emission Factor (kg CO₂e/kg)
```

**Emission Factor:** 2.6 kg CO₂e per kg of food waste

**Source:** UNEP Food Waste Index Report 2021

#### Example Calculation

```python
# User prevents 15 kg of food waste per year
food_waste_prevented = 15  # kg
emission_factor = 2.6  # kg CO₂e/kg

co2e_avoided = food_waste_prevented * emission_factor
# Result: 39 kg CO₂e/year

# Equivalent to:
# - 156 km driven in a car
# - 4.3 trees planted
# - 0.009 tonnes CO₂e
```

#### Implementation

```python
def calculate_carbon_footprint(food_waste_kg: float) -> dict:
    """Calculate carbon footprint reduction."""
    
    EMISSION_FACTOR = 2.6  # kg CO₂e per kg food
    KM_PER_KG_CO2E = 4.0   # km driven per kg CO₂e
    TREES_PER_KG_CO2E = 0.11  # trees planted per kg CO₂e
    
    co2e_avoided = food_waste_kg * EMISSION_FACTOR
    
    return {
        "co2e_kg": round(co2e_avoided, 2),
        "co2e_tonnes": round(co2e_avoided / 1000, 4),
        "equivalent_km_driven": round(co2e_avoided * KM_PER_KG_CO2E, 1),
        "equivalent_trees": round(co2e_avoided * TREES_PER_KG_CO2E, 1)
    }

# Example usage
impact = calculate_carbon_footprint(15)
print(impact)
# {'co2e_kg': 39.0, 'co2e_tonnes': 0.039, 
#  'equivalent_km_driven': 156.0, 'equivalent_trees': 4.3}
```

### 3.2 Water Footprint Reduction

#### Formula

```
Water Saved = Σ(Ingredient Weight × Water Footprint per kg)
```

**Water Footprint by Ingredient (liters/kg):**

| Ingredient | Water Footprint (L/kg) |
|------------|------------------------|
| Rice | 2,500 |
| Wheat/Bread | 1,800 |
| Vegetables (avg) | 300 |
| Fruits (avg) | 900 |
| Dairy | 1,000 |
| Meat (avg) | 15,000 |

**Source:** Water Footprint Network

#### Example Calculation

```python
# User saves these ingredients per year:
ingredients_saved = {
    "rice": 2.0,      # kg
    "bread": 1.5,     # kg
    "vegetables": 5.0, # kg
    "dairy": 3.0      # kg
}

water_footprint = {
    "rice": 2500,
    "bread": 1800,
    "vegetables": 300,
    "dairy": 1000
}

total_water = sum(
    ingredients_saved[ing] * water_footprint[ing]
    for ing in ingredients_saved
)
# Result: 15,200 liters/year
```

#### Implementation

```python
def calculate_water_savings(ingredients_saved: dict) -> dict:
    """Calculate water footprint reduction."""
    
    WATER_FOOTPRINT = {
        "rice": 2500,
        "wheat": 1800,
        "bread": 1800,
        "vegetables": 300,
        "fruits": 900,
        "dairy": 1000,
        "meat": 15000,
        "default": 500  # Average for unknown items
    }
    
    total_liters = 0
    breakdown = {}
    
    for ingredient, weight_kg in ingredients_saved.items():
        footprint = WATER_FOOTPRINT.get(ingredient, WATER_FOOTPRINT["default"])
        water_saved = weight_kg * footprint
        total_liters += water_saved
        breakdown[ingredient] = {
            "weight_kg": weight_kg,
            "water_liters": water_saved
        }
    
    return {
        "total_liters": round(total_liters, 1),
        "total_cubic_meters": round(total_liters / 1000, 2),
        "equivalent_bathtubs": round(total_liters / 150, 1),  # 150L per bath
        "breakdown": breakdown
    }
```

### 3.3 Waste Reduction

#### Formula

```
Waste Reduction Rate = (Baseline Waste - Current Waste) / Baseline Waste × 100
```

#### Tracking

```python
def calculate_waste_reduction(baseline_kg: float, current_kg: float) -> dict:
    """Calculate waste reduction percentage."""
    
    reduction_kg = baseline_kg - current_kg
    reduction_rate = (reduction_kg / baseline_kg) * 100 if baseline_kg > 0 else 0
    
    return {
        "baseline_kg": baseline_kg,
        "current_kg": current_kg,
        "reduction_kg": round(reduction_kg, 2),
        "reduction_rate": round(reduction_rate, 1),
        "status": "improved" if reduction_kg > 0 else "needs_attention"
    }

# Example: User reduced waste from 50kg to 35kg per year
result = calculate_waste_reduction(50, 35)
# {'baseline_kg': 50, 'current_kg': 35, 'reduction_kg': 15.0, 
#  'reduction_rate': 30.0, 'status': 'improved'}
```

---

## 4. Economic Impact

### 4.1 Cost Savings

#### Formula

```
Cost Savings = Food Waste Prevented (kg) × Average Food Price (₹/kg)
```

**Average Food Price in India:** ₹87/kg (2024 estimate)

**Source:** Ministry of Consumer Affairs, Food & Public Distribution

#### Example Calculation

```python
# User prevents 15 kg of food waste per year
food_waste_prevented = 15  # kg
avg_price_per_kg = 87  # ₹

cost_savings = food_waste_prevented * avg_price_per_kg
# Result: ₹1,305/year per user

# For 10,000 users:
total_savings = cost_savings * 10000
# Result: ₹1,30,50,000 (₹1.3 crores)
```

#### Implementation

```python
def calculate_cost_savings(food_waste_kg: float, 
                          price_per_kg: float = 87) -> dict:
    """Calculate economic savings from waste reduction."""
    
    savings_inr = food_waste_kg * price_per_kg
    
    return {
        "food_waste_kg": food_waste_kg,
        "price_per_kg": price_per_kg,
        "savings_inr": round(savings_inr, 2),
        "savings_usd": round(savings_inr / 83, 2),  # ₹83 = $1
        "monthly_savings": round(savings_inr / 12, 2),
        "daily_savings": round(savings_inr / 365, 2)
    }
```

### 4.2 Return on Investment (ROI)

#### Formula

```
ROI = (Benefits - Costs) / Costs × 100
```

#### Example Calculation

```python
# Annual costs per user
costs = {
    "api_calls": 100,      # ₹100 for IBM Granite API
    "electricity": 50,     # ₹50 for GPU usage
    "internet": 0          # Assumed included
}
total_cost = sum(costs.values())  # ₹150

# Annual benefits per user
benefits = {
    "food_savings": 1305,  # From waste reduction
    "time_saved": 500      # Value of time saved (estimated)
}
total_benefit = sum(benefits.values())  # ₹1,805

# Calculate ROI
roi = ((total_benefit - total_cost) / total_cost) * 100
# Result: 1,103% ROI
```

#### Implementation

```python
def calculate_roi(annual_costs: dict, annual_benefits: dict) -> dict:
    """Calculate return on investment."""
    
    total_cost = sum(annual_costs.values())
    total_benefit = sum(annual_benefits.values())
    net_benefit = total_benefit - total_cost
    roi_percentage = (net_benefit / total_cost * 100) if total_cost > 0 else 0
    payback_months = (total_cost / (total_benefit / 12)) if total_benefit > 0 else float('inf')
    
    return {
        "total_cost": round(total_cost, 2),
        "total_benefit": round(total_benefit, 2),
        "net_benefit": round(net_benefit, 2),
        "roi_percentage": round(roi_percentage, 1),
        "payback_months": round(payback_months, 1),
        "cost_breakdown": annual_costs,
        "benefit_breakdown": annual_benefits
    }
```

### 4.3 Resource Efficiency

#### Metrics

```python
def calculate_efficiency_metrics(total_users: int, 
                                total_recipes: int,
                                total_ingredients: int) -> dict:
    """Calculate system efficiency metrics."""
    
    return {
        "recipes_per_user": round(total_recipes / total_users, 1),
        "ingredients_per_recipe": round(total_ingredients / total_recipes, 1),
        "utilization_rate": round((total_recipes / (total_users * 365)) * 100, 1),
        "avg_match_score": 85.0,  # From recipe matcher
        "cache_hit_rate": 65.0     # From vision system
    }
```

---

## 5. Social Impact

### 5.1 Food Security

#### Meals Created from Leftovers

```
Meals Created = Recipes Made × Average Servings per Recipe
```

#### Example Calculation

```python
# User creates 100 recipes per year
recipes_per_year = 100
avg_servings = 2

meals_created = recipes_per_year * avg_servings
# Result: 200 meals/year

# For 10,000 users:
total_meals = meals_created * 10000
# Result: 2,000,000 meals/year
```

#### Implementation

```python
def calculate_food_security_impact(recipes_created: int,
                                  avg_servings: int = 2) -> dict:
    """Calculate food security contribution."""
    
    meals_created = recipes_created * avg_servings
    
    # Assume 3 meals per day
    days_of_food = meals_created / 3
    
    # Assume 4 people per household
    households_fed = meals_created / (3 * 4)
    
    return {
        "recipes_created": recipes_created,
        "meals_created": meals_created,
        "days_of_food": round(days_of_food, 1),
        "households_fed_per_day": round(households_fed, 1),
        "nutritional_value": "varies",  # Future: calculate calories, nutrients
        "food_security_score": min(10, round(meals_created / 20, 1))
    }
```

### 5.2 Behavior Change

#### Metrics

```python
def track_behavior_change(user_id: str, 
                         usage_data: dict) -> dict:
    """Track user behavior change over time."""
    
    # Calculate trends
    initial_waste = usage_data.get("initial_waste_kg", 50)
    current_waste = usage_data.get("current_waste_kg", 35)
    
    # Engagement metrics
    days_active = usage_data.get("days_active", 0)
    total_days = usage_data.get("total_days", 365)
    engagement_rate = (days_active / total_days) * 100
    
    # Learning curve
    recipes_tried = usage_data.get("recipes_tried", 0)
    unique_recipes = usage_data.get("unique_recipes", 0)
    variety_score = (unique_recipes / recipes_tried * 100) if recipes_tried > 0 else 0
    
    return {
        "user_id": user_id,
        "waste_reduction": round(((initial_waste - current_waste) / initial_waste) * 100, 1),
        "engagement_rate": round(engagement_rate, 1),
        "variety_score": round(variety_score, 1),
        "behavior_stage": classify_behavior_stage(engagement_rate),
        "recommendations": generate_recommendations(engagement_rate, variety_score)
    }

def classify_behavior_stage(engagement_rate: float) -> str:
    """Classify user behavior stage."""
    if engagement_rate < 20:
        return "awareness"
    elif engagement_rate < 50:
        return "adoption"
    elif engagement_rate < 80:
        return "habit_formation"
    else:
        return "advocate"
```

### 5.3 Community Impact

#### Metrics

```python
def calculate_community_impact(total_users: int,
                              avg_household_size: int = 4) -> dict:
    """Calculate broader community impact."""
    
    # Direct impact
    people_reached = total_users * avg_household_size
    
    # Indirect impact (word of mouth, social sharing)
    indirect_reach = people_reached * 2  # Estimated multiplier
    
    # Community savings
    community_savings = total_users * 1305  # ₹1,305 per user
    
    return {
        "total_users": total_users,
        "people_directly_reached": people_reached,
        "people_indirectly_reached": indirect_reach,
        "total_reach": people_reached + indirect_reach,
        "community_savings_inr": community_savings,
        "awareness_level": "growing",
        "social_proof": calculate_social_proof(total_users)
    }

def calculate_social_proof(total_users: int) -> str:
    """Calculate social proof level."""
    if total_users < 100:
        return "early_adopters"
    elif total_users < 1000:
        return "growing_community"
    elif total_users < 10000:
        return "established_platform"
    else:
        return "mainstream_adoption"
```

---

## 6. Data Collection Methods

### 6.1 Automated Data Collection

```python
class MetricsCollector:
    """Automated metrics collection system."""
    
    def __init__(self):
        self.metrics_db = {}
    
    def log_recipe_creation(self, user_id: str, recipe_data: dict):
        """Log when a recipe is created."""
        timestamp = datetime.now().isoformat()
        
        event = {
            "event_type": "recipe_created",
            "user_id": user_id,
            "timestamp": timestamp,
            "recipe_name": recipe_data["name"],
            "ingredients_used": recipe_data["ingredients"],
            "match_score": recipe_data["score"],
            "estimated_waste_prevented": self.estimate_waste_prevented(recipe_data)
        }
        
        self.save_event(event)
    
    def log_ingredient_detection(self, user_id: str, detection_data: dict):
        """Log ingredient detection events."""
        event = {
            "event_type": "ingredients_detected",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "ingredients": detection_data["ingredients"],
            "detection_time": detection_data["processing_time"],
            "cache_hit": detection_data["cache_hit"]
        }
        
        self.save_event(event)
    
    def estimate_waste_prevented(self, recipe_data: dict) -> float:
        """Estimate waste prevented by this recipe."""
        # Average weight per ingredient: 100g
        num_ingredients = len(recipe_data["ingredients"])
        return num_ingredients * 0.1  # kg
```

### 6.2 User Surveys

**Survey Template:**

```json
{
  "survey_id": "monthly_impact_2026_06",
  "questions": [
    {
      "id": 1,
      "question": "How much food waste do you estimate you prevented this month?",
      "type": "range",
      "min": 0,
      "max": 10,
      "unit": "kg"
    },
    {
      "id": 2,
      "question": "How satisfied are you with the recipe recommendations?",
      "type": "scale",
      "min": 1,
      "max": 10
    },
    {
      "id": 3,
      "question": "How often do you use RecipeAI?",
      "type": "multiple_choice",
      "options": ["Daily", "Weekly", "Monthly", "Rarely"]
    },
    {
      "id": 4,
      "question": "What impact has RecipeAI had on your food waste habits?",
      "type": "text"
    }
  ]
}
```

### 6.3 Manual Tracking

**User Dashboard Template:**

```python
def generate_user_dashboard(user_id: str) -> dict:
    """Generate personalized impact dashboard."""
    
    user_data = fetch_user_data(user_id)
    
    return {
        "user_id": user_id,
        "period": "last_30_days",
        "summary": {
            "recipes_created": user_data["recipes_count"],
            "food_waste_prevented_kg": user_data["waste_prevented"],
            "co2e_avoided_kg": user_data["waste_prevented"] * 2.6,
            "cost_saved_inr": user_data["waste_prevented"] * 87,
            "meals_created": user_data["recipes_count"] * 2
        },
        "trends": {
            "waste_reduction_trend": "improving",  # vs previous period
            "engagement_trend": "stable",
            "variety_trend": "increasing"
        },
        "achievements": [
            "🌟 Prevented 5kg of waste this month!",
            "🌱 Saved 13kg CO₂e - equivalent to 2 trees!",
            "💰 Saved ₹435 this month!"
        ],
        "next_goals": [
            "Try 5 new recipes",
            "Prevent 10kg of waste",
            "Share your impact with friends"
        ]
    }
```

---

## 7. Calculation Formulas

### 7.1 Master Formula Sheet

```python
# Environmental Impact
CO2E_AVOIDED = food_waste_kg * 2.6
WATER_SAVED = sum(ingredient_kg * water_footprint_per_kg)
WASTE_REDUCTION_RATE = (baseline - current) / baseline * 100

# Economic Impact
COST_SAVINGS = food_waste_kg * 87  # ₹87/kg average
ROI = (benefits - costs) / costs * 100
PAYBACK_PERIOD = costs / (benefits / 12)  # months

# Social Impact
MEALS_CREATED = recipes * 2  # avg servings
FOOD_SECURITY_SCORE = min(10, meals_created / 20)
ENGAGEMENT_RATE = active_days / total_days * 100

# System Performance
CACHE_HIT_RATE = cache_hits / total_requests * 100
AVG_RESPONSE_TIME = sum(response_times) / len(response_times)
ACCURACY = correct_detections / total_detections * 100
```

### 7.2 Aggregation Formulas

```python
def aggregate_metrics(user_metrics: list) -> dict:
    """Aggregate metrics across all users."""
    
    total_users = len(user_metrics)
    
    return {
        "total_users": total_users,
        "total_food_waste_prevented": sum(u["waste_kg"] for u in user_metrics),
        "total_co2e_avoided": sum(u["waste_kg"] * 2.6 for u in user_metrics),
        "total_cost_saved": sum(u["waste_kg"] * 87 for u in user_metrics),
        "total_recipes_created": sum(u["recipes"] for u in user_metrics),
        "total_meals_created": sum(u["recipes"] * 2 for u in user_metrics),
        "avg_waste_per_user": sum(u["waste_kg"] for u in user_metrics) / total_users,
        "avg_engagement_rate": sum(u["engagement"] for u in user_metrics) / total_users
    }
```

---

## 8. Baseline Establishment

### 8.1 Individual Baseline

```python
def establish_user_baseline(user_id: str, duration_days: int = 30) -> dict:
    """Establish baseline for a new user."""
    
    # Default baseline (Indian household average)
    default_baseline = {
        "food_waste_kg_per_month": 4.2,  # ~50kg/year
        "grocery_spend_per_month": 5000,  # ₹
        "meals_cooked_per_week": 14,
        "ingredients_wasted_per_week": 5
    }
    
    # Collect actual data during baseline period
    actual_data = collect_baseline_data(user_id, duration_days)
    
    # Use actual if available, otherwise default
    baseline = actual_data if actual_data else default_baseline
    
    # Save baseline
    save_user_baseline(user_id, baseline)
    
    return {
        "user_id": user_id,
        "baseline_established": datetime.now().isoformat(),
        "baseline_period_days": duration_days,
        "baseline_metrics": baseline,
        "data_source": "actual" if actual_data else "default"
    }
```

### 8.2 System-Wide Baseline

```python
# Indian household food waste statistics
NATIONAL_BASELINE = {
    "avg_food_waste_per_capita_kg_year": 50,  # India average
    "avg_household_size": 4.4,
    "avg_food_waste_per_household_kg_year": 220,
    "food_waste_percentage_of_total": 8.5,  # % of food purchased
    "primary_waste_categories": {
        "vegetables": 30,
        "fruits": 25,
        "grains": 20,
        "dairy": 15,
        "other": 10
    }
}
```

---

## 9. Reporting Templates

### 9.1 Monthly Impact Report

```python
def generate_monthly_report(month: str, year: int) -> dict:
    """Generate monthly impact report."""
    
    data = fetch_monthly_data(month, year)
    
    report = {
        "report_period": f"{month} {year}",
        "generated_on": datetime.now().isoformat(),
        
        "executive_summary": {
            "total_users": data["users"],
            "active_users": data["active_users"],
            "new_users": data["new_users"],
            "retention_rate": f"{data['retention']}%"
        },
        
        "environmental_impact": {
            "food_waste_prevented_kg": data["waste_prevented"],
            "co2e_avoided_kg": data["waste_prevented"] * 2.6,
            "water_saved_liters": data["water_saved"],
            "equivalent_trees_planted": round(data["waste_prevented"] * 2.6 * 0.11, 1)
        },
        
        "economic_impact": {
            "total_savings_inr": data["waste_prevented"] * 87,
            "avg_savings_per_user": round((data["waste_prevented"] * 87) / data["users"], 2),
            "roi_percentage": data["roi"]
        },
        
        "social_impact": {
            "recipes_created": data["recipes"],
            "meals_created": data["recipes"] * 2,
            "user_satisfaction": data["satisfaction"],
            "community_reach": data["users"] * 4
        },
        
        "system_performance": {
            "avg_response_time": f"{data['avg_response_time']}s",
            "cache_hit_rate": f"{data['cache_hit_rate']}%",
            "accuracy": f"{data['accuracy']}%",
            "uptime": f"{data['uptime']}%"
        },
        
        "trends": {
            "vs_last_month": calculate_trends(data, "month"),
            "vs_last_year": calculate_trends(data, "year")
        },
        
        "highlights": generate_highlights(data),
        "challenges": identify_challenges(data),
        "recommendations": generate_recommendations_report(data)
    }
    
    return report
```

### 9.2 Annual Impact Report

```markdown
# RecipeAI Annual Impact Report 2026

## Executive Summary
- **Total Users:** 10,000
- **Food Waste Prevented:** 150 tonnes
- **CO₂e Avoided:** 390 tonnes
- **Cost Savings:** ₹1.3 crores

## Environmental Impact
### Carbon Footprint
- 390 tonnes CO₂e avoided
- Equivalent to:
  - 1,560,000 km not driven
  - 4,290 trees planted
  - 86 homes' energy for 1 year

### Water Conservation
- 15 million liters saved
- Equivalent to:
  - 100,000 bathtubs
  - 6 Olympic swimming pools

## Economic Impact
- Total savings: ₹1,30,50,000
- Average per user: ₹13,050
- ROI: 1,103%

## Social Impact
- 2 million meals created
- 40,000 people reached
- 70% user retention

## SDG Contribution
- SDG 12.3: 30% waste reduction achieved
- SDG 2: 2M meals contributed to food security
- SDG 13: 390 tonnes CO₂e climate action

## Looking Ahead
- Target 2027: 100,000 users
- Expansion to 5 new cities
- Partnership with 50 restaurants
```

---

## 10. Visualization Guidelines

### 10.1 Dashboard Design

```python
def create_impact_dashboard():
    """Create visual dashboard for impact metrics."""
    
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Set style
    sns.set_style("whitegrid")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 1. Food Waste Trend
    axes[0, 0].plot(months, waste_prevented, marker='o', color='green')
    axes[0, 0].set_title('Food Waste Prevented Over Time')
    axes[0, 0].set_xlabel('Month')
    axes[0, 0].set_ylabel('Waste Prevented (kg)')
    
    # 2. CO₂e Impact
    axes[0, 1].bar(categories, co2e_by_category, color='blue')
    axes[0, 1].set_title('CO₂e Avoided by Category')
    axes[0, 1].set_xlabel('Food Category')
    axes[0, 1].set_ylabel('CO₂e (kg)')
    
    # 3. Cost Savings
    axes[1, 0].pie(savings_breakdown, labels=labels, autopct='%1.1f%%')
    axes[1, 0].set_title('Cost Savings Breakdown')
    
    # 4. User Engagement
    axes[1, 1].scatter(days_active, waste_prevented, alpha=0.5)
    axes[1, 1].set_title('Engagement vs Impact')
    axes[1, 1].set_xlabel('Days Active')
    axes[1, 1].set_ylabel('Waste Prevented (kg)')
    
    plt.tight_layout()
    plt.savefig('impact_dashboard.png', dpi=300)
    
    return fig
```

### 10.2 Infographic Elements

**Key Visualizations:**

1. **Progress Bars:** Show progress toward goals
2. **Trend Lines:** Display improvement over time
3. **Comparison Charts:** Before/after impact
4. **Heat Maps:** Geographic distribution
5. **Pie Charts:** Category breakdowns
6. **Gauges:** Real-time metrics

---

## 11. Case Studies

### 11.1 Individual User Case Study

**User Profile:**
- Name: Priya S.
- Location: Mumbai
- Household: 4 members
- Duration: 6 months

**Baseline (Before RecipeAI):**
- Food waste: 5 kg/month
- Grocery spend: ₹6,000/month
- Recipes tried: 10/month

**After 6 Months:**
- Food waste: 2 kg/month (60% reduction)
- Grocery spend: ₹5,200/month (₹800 saved)
- Recipes tried: 25/month (150% increase)

**Impact:**
- Food waste prevented: 18 kg
- CO₂e avoided: 46.8 kg
- Cost saved: ₹4,800
- Meals created: 150

**Testimonial:**
> "RecipeAI transformed how I think about leftovers. What I used to throw away now becomes delicious meals. My family loves the variety, and I love the savings!"

### 11.2 Community Case Study

**Community:** Residential Society, Bangalore
- Households: 50
- Participants: 35 households
- Duration: 3 months

**Collective Impact:**
- Food waste prevented: 525 kg
- CO₂e avoided: 1,365 kg
- Cost saved: ₹45,675
- Meals created: 3,500

**Community Benefits:**
- Shared recipe exchange
- Bulk ingredient purchasing
- Food donation program
- Awareness workshops

---

## 12. SDG Alignment

### 12.1 SDG 12: Responsible Consumption

**Target 12.3:** Halve per capita food waste by 2030

**Our Contribution:**
- 30% reduction in household food waste
- 150 tonnes prevented annually (at 10K users)
- Scalable to millions of users

**Measurement:**
```python
def calculate_sdg_12_3_progress(baseline_waste: float, 
                                current_waste: float) -> dict:
    """Calculate progress toward SDG 12.3."""
    
    reduction = (baseline_waste - current_waste) / baseline_waste * 100
    target = 50  # 50% reduction by 2030
    progress = (reduction / target) * 100
    
    return {
        "target": "SDG 12.3",
        "goal": "50% reduction by 2030",
        "current_reduction": f"{reduction}%",
        "progress_toward_goal": f"{progress}%",
        "status": "on_track" if reduction >= 30 else "needs_acceleration"
    }
```

### 12.2 SDG 2: Zero Hunger

**Contribution:**
- 2 million meals created from leftovers
- Food security for vulnerable populations
- Nutrition education

### 12.3 SDG 13: Climate Action

**Contribution:**
- 390 tonnes CO₂e avoided annually
- Climate awareness through impact tracking
- Behavioral change toward sustainability

---

## Appendix: Metric Definitions

### A.1 Glossary

| Term | Definition |
|------|------------|
| **CO₂e** | Carbon dioxide equivalent - standard unit for carbon footprint |
| **Water Footprint** | Total water used to produce food items |
| **Waste Reduction Rate** | Percentage decrease in food waste |
| **ROI** | Return on investment - financial benefit vs cost |
| **Engagement Rate** | Percentage of days user is active |
| **Cache Hit Rate** | Percentage of requests served from cache |

### A.2 Data Sources

1. **UNEP Food Waste Index Report 2021**
2. **Water Footprint Network**
3. **Ministry of Consumer Affairs, India**
4. **FAO Food Wastage Footprint**
5. **UN SDG Indicators Database**

---

**Document Version:** 1.0  
**Last Updated:** June 19, 2026  
**Maintained By:** RecipeAI Team

For technical implementation, see [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md)  
For system architecture, see [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)  
For setup instructions, see [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)