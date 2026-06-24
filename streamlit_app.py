"""
AI-Powered Food Waste Reduction Assistant
Streamlit Web Application
"""

import streamlit as st
import os
from PIL import Image
import time
from typing import List, Dict, Optional

# Import our modules
from vision import extract_ingredients
from recipe_matcher import find_best_recipes
from sustainability_engine import generate_full_sustainability_report
from recommendation_engine import get_recipe_recommendations_with_analysis
from granite import (
    get_recommendation,
    generate_sdg_impact_analysis,
    generate_sustainability_tips,
    check_ollama_connection,
    check_model_available
)


# Page configuration
st.set_page_config(
    page_title="Food Waste Reduction Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #558B2F;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F1F8E9;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #66BB6A;
        margin: 1rem 0;
    }
    .recipe-card {
        background-color: #E8F5E9;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px solid #81C784;
    }
    .ingredient-tag {
        display: inline-block;
        background-color: #C8E6C9;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        margin: 0.2rem;
        font-size: 0.9rem;
    }
    .sdg-badge {
        background-color: #1976D2;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .success-message {
        background-color: #C8E6C9;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
    .warning-message {
        background-color: #FFF9C4;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #FFC107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def display_header():
    """Display application header"""
    st.markdown('<div class="main-header">🌱 AI-Powered Food Waste Reduction Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Transform your ingredients into sustainable meals • Reduce waste • Save the planet</div>', unsafe_allow_html=True)


def display_system_status():
    """Display system status in sidebar"""
    st.sidebar.markdown("### 🔧 System Status")
    
    # Check Ollama connection
    ollama_status = check_ollama_connection()
    granite_status = check_model_available()
    
    if ollama_status and granite_status:
        st.sidebar.success("✅ Granite AI: Connected")
    elif ollama_status:
        st.sidebar.warning("⚠️ Granite AI: Model not found")
    else:
        st.sidebar.error("❌ Granite AI: Offline (using fallback)")
    
    st.sidebar.info("ℹ️ Vision AI: Qwen2.5-VL Active")


def display_ingredients(ingredients: List[str]):
    """Display detected ingredients"""
    st.markdown("### 🥗 Detected Ingredients")
    
    if not ingredients:
        st.warning("No ingredients detected. Please try another image.")
        return
    
    # Display as tags
    html_tags = "".join([f'<span class="ingredient-tag">{ing}</span>' for ing in ingredients])
    st.markdown(f'<div>{html_tags}</div>', unsafe_allow_html=True)
    
    st.metric("Total Ingredients", len(ingredients))


def display_recipe_matches(recipes: List[Dict], top_n: int = 5):
    """Display recipe matches"""
    st.markdown("### 🍳 Recipe Matches")
    
    if not recipes:
        st.warning("No recipe matches found.")
        return
    
    for i, recipe in enumerate(recipes[:top_n], 1):
        with st.expander(f"#{i} {recipe['name']} - {recipe['score']}% Match", expanded=(i == 1)):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**✅ Matched Ingredients:**")
                if recipe['matched']:
                    for ing in recipe['matched']:
                        st.markdown(f"- {ing}")
                else:
                    st.markdown("None")
            
            with col2:
                st.markdown("**❌ Missing Ingredients:**")
                if recipe['missing']:
                    for ing in recipe['missing']:
                        st.markdown(f"- {ing}")
                else:
                    st.markdown("None")
            
            st.markdown(f"**🎯 Target:** {recipe.get('target', 'General')}")


def display_top_recommendation(recommendation: Dict, user_ingredients: List[str]):
    """Display the top recommended recipe with full details"""
    st.markdown("### ⭐ Top Recommendation")
    
    st.markdown(f"""
    <div class="recipe-card">
        <h2 style="color: #2E7D32; margin-top: 0;">{recommendation['name']}</h2>
        <p style="font-size: 1.1rem;"><strong>Match Score:</strong> {recommendation['score']}%</p>
        <p style="font-size: 1.1rem;"><strong>Priority Score:</strong> {recommendation.get('priority_score', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display recommendation reason
    if 'recommendation_reason' in recommendation:
        st.info(f"💡 {recommendation['recommendation_reason']}")
    
    # Display ingredients breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ Using from your ingredients:")
        for ing in recommendation['matched']:
            st.markdown(f"- ✓ {ing}")
    
    with col2:
        st.markdown("#### 🛒 Need to buy:")
        if recommendation['missing']:
            for ing in recommendation['missing']:
                st.markdown(f"- {ing}")
                # Show substitutions if available
                if 'substitutions' in recommendation and ing in recommendation['substitutions']:
                    subs = recommendation['substitutions'][ing]
                    st.markdown(f"  *Can substitute with: {', '.join(subs)}*")
        else:
            st.success("No additional ingredients needed! 🎉")


def display_sustainability_metrics(sustainability_report: Dict):
    """Display sustainability metrics"""
    st.markdown("### 🌍 Sustainability Metrics")
    
    # Main metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Ingredient Utilization",
            f"{sustainability_report['ingredient_utilization']}%",
            help="Percentage of your ingredients used in this recipe"
        )
    
    with col2:
        waste_score = sustainability_report['waste_reduction']['score']
        st.metric(
            "Waste Reduction",
            f"{waste_score}/10",
            help="How effectively this recipe reduces food waste"
        )
    
    with col3:
        sustainability_score = sustainability_report['sustainability']['overall_score']
        st.metric(
            "Sustainability Score",
            f"{sustainability_score}/100",
            help="Overall sustainability rating"
        )
    
    with col4:
        co2_saved = sustainability_report['co2_impact']['net_co2_saved']
        st.metric(
            "CO₂ Saved",
            f"{co2_saved} kg",
            help="Estimated CO2 emissions prevented"
        )
    
    # Detailed breakdown
    with st.expander("📊 Detailed Sustainability Breakdown"):
        st.markdown("#### Waste Reduction Analysis")
        st.write(sustainability_report['waste_reduction']['explanation'])
        
        st.markdown("#### Sustainability Components")
        breakdown = sustainability_report['sustainability']['breakdown']
        st.write(f"- **Ingredient Availability:** {breakdown['availability']}/40")
        st.write(f"- **Waste Targeting:** {breakdown['waste_targeting']}/30")
        st.write(f"- **Resource Efficiency:** {breakdown['resource_efficiency']}/30")
        
        st.markdown("#### CO₂ Impact Details")
        co2 = sustainability_report['co2_impact']
        st.write(f"- **CO₂ saved from waste:** {co2['co2_saved_from_waste']} kg")
        st.write(f"- **CO₂ from cooking:** {co2['co2_from_cooking']} kg")
        st.write(f"- **Net CO₂ saved:** {co2['net_co2_saved']} kg")
        st.write(f"- **Equivalent to:** {co2['equivalent_km_driven']} km not driven")


def display_sdg_impact(sustainability_report: Dict, recipe_name: str):
    """Display SDG 12 impact analysis"""
    st.markdown("### 🎯 UN SDG 12 Impact")
    
    sdg = sustainability_report['sdg_alignment']
    
    # SDG Badge
    st.markdown(f'<div class="sdg-badge">SDG 12: Responsible Consumption & Production</div>', unsafe_allow_html=True)
    
    # Impact metrics
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric("SDG Alignment Score", f"{sdg['sdg_score']}/100")
        st.markdown(f"**Impact Level:** {sdg['impact_level']}")
    
    with col2:
        st.markdown("**Description:**")
        st.write(sdg['description'])
        
        st.markdown("**Targets Addressed:**")
        for target in sdg['targets_addressed']:
            st.write(f"- {target}")
    
    # Get AI-generated analysis from Granite
    with st.spinner("Generating AI-powered SDG impact analysis..."):
        matched_ingredients = sustainability_report['summary']['ingredients_used']
        waste_score = sustainability_report['waste_reduction']['score']
        co2_saved = sustainability_report['co2_impact']['net_co2_saved']
        
        # Create a list of ingredient names (we'll use matched from the recipe)
        ingredients_list = [f"ingredient_{i}" for i in range(matched_ingredients)]
        
        ai_analysis = generate_sdg_impact_analysis(
            recipe_name,
            ingredients_list,
            waste_score,
            co2_saved
        )
        
        st.markdown("#### 🤖 AI-Powered Impact Analysis")
        st.info(ai_analysis)


def display_granite_recommendation(ingredients: List[str], recipe_names: List[str], top_recipe: Dict):
    """Display Granite AI recommendation"""
    st.markdown("### 🤖 AI Chef's Recommendation")
    
    with st.spinner("Consulting AI Chef powered by IBM Granite..."):
        granite_response = get_recommendation(ingredients, recipe_names, top_recipe)
        
        st.markdown(f"""
        <div class="metric-card">
            <pre style="white-space: pre-wrap; font-family: 'Segoe UI', sans-serif; font-size: 0.95rem;">
{granite_response}
            </pre>
        </div>
        """, unsafe_allow_html=True)


def display_sustainability_tips(user_ingredients: List[str], used_ingredients: List[str], recipe_target: str):
    """Display sustainability tips for unused ingredients"""
    unused = list(set(user_ingredients) - set(used_ingredients))
    
    if not unused:
        st.success("🎉 Excellent! You're using all your ingredients efficiently!")
        return
    
    st.markdown("### 💡 Sustainability Tips")
    st.markdown(f"**Unused ingredients:** {', '.join(unused)}")
    
    with st.spinner("Generating personalized tips..."):
        tips = generate_sustainability_tips(unused, recipe_target)
        st.markdown(tips)


def main():
    """Main application function"""
    display_header()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📸 Upload Image")
        display_system_status()
        
        st.markdown("---")
        st.markdown("### About")
        st.info("""
        This AI-powered assistant helps you:
        - 🔍 Identify ingredients from photos
        - 🍳 Find recipes that reduce waste
        - 🌍 Calculate sustainability impact
        - 🎯 Align with UN SDG 12
        """)
        
        st.markdown("---")
        st.markdown("### Settings")
        top_n_recipes = st.slider("Number of recipes to show", 3, 10, 5)
    
    # Main content area
    uploaded_file = st.file_uploader(
        "Upload a photo of your ingredients",
        type=["jpg", "jpeg", "png"],
        help="Take a clear photo of your fridge or ingredients"
    )
    
    # Sample images option
    st.markdown("**Or try a sample image:**")
    col1, col2 = st.columns(2)
    
    sample_selected = None
    with col1:
        if st.button("📷 Sample 1 (Fridge)", use_container_width=True):
            sample_selected = "samples/fridge_1.jpeg"
    
    with col2:
        if st.button("📷 Sample 2 (Fridge)", use_container_width=True):
            sample_selected = "samples/fridge_2.png"
    
    # Process image
    image_path = None
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        image_path = f"temp_{uploaded_file.name}"
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
    
    elif sample_selected:
        image_path = sample_selected
        if os.path.exists(image_path):
            image = Image.open(image_path)
            st.image(image, caption="Sample Image", use_container_width=True)
    
    # Process if we have an image
    if image_path:
        st.markdown("---")
        
        # Step 1: Extract ingredients
        with st.spinner("🔍 Analyzing image with Qwen Vision AI..."):
            start_time = time.time()
            ingredients = extract_ingredients(image_path)
            extraction_time = time.time() - start_time
        
        if ingredients:
            st.success(f"✅ Detected {len(ingredients)} ingredients in {extraction_time:.2f}s")
            display_ingredients(ingredients)
            
            st.markdown("---")
            
            # Step 2: Find recipe matches
            with st.spinner("🔍 Finding recipe matches..."):
                recipes = find_best_recipes(ingredients, top_n=top_n_recipes)
            
            if recipes:
                display_recipe_matches(recipes, top_n=top_n_recipes)
                
                st.markdown("---")
                
                # Step 3: Get recommendations
                with st.spinner("🤔 Analyzing recommendations..."):
                    recommendations = get_recipe_recommendations_with_analysis(recipes, ingredients)
                
                top_recipe = recommendations['top_recommendation']
                
                if top_recipe:
                    display_top_recommendation(top_recipe, ingredients)
                    
                    st.markdown("---")
                    
                    # Step 4: Calculate sustainability metrics
                    with st.spinner("🌍 Calculating sustainability metrics..."):
                        sustainability_report = generate_full_sustainability_report(
                            ingredients,
                            top_recipe
                        )
                    
                    display_sustainability_metrics(sustainability_report)
                    
                    st.markdown("---")
                    
                    # Step 5: SDG Impact
                    display_sdg_impact(sustainability_report, top_recipe['name'])
                    
                    st.markdown("---")
                    
                    # Step 6: Granite AI Recommendation
                    recipe_names = [r['name'] for r in recipes[:5]]
                    display_granite_recommendation(ingredients, recipe_names, top_recipe)
                    
                    st.markdown("---")
                    
                    # Step 7: Sustainability Tips
                    display_sustainability_tips(
                        ingredients,
                        top_recipe['matched'],
                        top_recipe.get('target', 'General')
                    )
                    
                else:
                    st.error("Could not generate recommendation. Please try again.")
            else:
                st.warning("No recipe matches found for your ingredients.")
        else:
            st.error("Could not detect ingredients. Please try another image.")
        
        # Clean up temporary file
        if uploaded_file and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except:
                pass
    
    else:
        # Welcome message
        st.markdown("""
        <div class="success-message">
            <h3>👋 Welcome to the Food Waste Reduction Assistant!</h3>
            <p>Get started by uploading a photo of your ingredients or trying a sample image.</p>
            <p><strong>How it works:</strong></p>
            <ol>
                <li>📸 Upload or select a photo of your ingredients</li>
                <li>🔍 AI identifies what you have</li>
                <li>🍳 Get personalized recipe recommendations</li>
                <li>🌍 See your sustainability impact</li>
                <li>🎯 Contribute to UN SDG 12</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

# Made with Bob
