"""
FastAPI Backend for RecipeAI
Provides RESTful API endpoints for ingredient detection, recipe matching,
sustainability analysis, and AI recommendations
"""

import os
import sys
import time
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Get the project root directory (parent of backend/)
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = Path(__file__).parent

# Add parent directory to path to import modules
sys.path.insert(0, str(PROJECT_ROOT))

from vision import extract_ingredients, get_image_hash, load_cache
from recipe_matcher import find_best_recipes
from granite import get_recommendation, generate_sdg_impact_analysis, generate_sustainability_tips
from sustainability_engine import generate_full_sustainability_report
from recommendation_engine import get_recipe_recommendations_with_analysis
from config import MODEL_MODE, start_ssh_tunnel, stop_ssh_tunnel

# Initialize FastAPI app
app = FastAPI(
    title="Byte2Bite API",
    description="AI-powered recipe recommendation system with sustainability analysis",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    if MODEL_MODE == "cloud":
        start_ssh_tunnel()

@app.on_event("shutdown")
async def shutdown_event():
    if MODEL_MODE == "cloud":
        stop_ssh_tunnel()


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory (use /tmp on Vercel since filesystem is read-only)
if os.getenv("VERCEL"):
    UPLOAD_DIR = Path("/tmp/uploads")
else:
    UPLOAD_DIR = BACKEND_DIR / "uploads"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files for serving uploaded images
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Pydantic models for request/response
class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: float

class IngredientItem(BaseModel):
    name: str
    count: int

class IngredientsResponse(BaseModel):
    ingredients: List[IngredientItem]
    processing_time: float
    cache_hit: bool
    labeled_image_url: Optional[str] = None

class RecipeMatch(BaseModel):
    name: str
    score: float
    matched: List[str]
    missing: List[str]
    target: str
    dietary: str
    ingredients_used: int
    utilization: float
    quantity_info: Dict[str, Any]
    cuisine: str
    difficulty: str
    time: str
    servings: int
    description: str

class RecipesResponse(BaseModel):
    recipes: List[RecipeMatch]
    processing_time: float

class SustainabilityResponse(BaseModel):
    report: Dict[str, Any]
    processing_time: float

class RecommendationResponse(BaseModel):
    recommendation: str
    processing_time: float

class FullAnalysisResponse(BaseModel):
    ingredients: List[IngredientItem]
    recipes: List[Dict[str, Any]]
    top_recipe: Optional[Dict[str, Any]]
    sustainability_report: Dict[str, Any]
    ai_recommendation: str
    sdg_analysis: Optional[str]
    sustainability_tips: Optional[str]
    total_processing_time: float
    stages: Dict[str, float]

class ProcessingStatus(BaseModel):
    stage: str
    message: str
    progress: int
    timestamp: float

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []
    ingredients: List[str] = []
    current_recipe: Optional[str] = None


# Global processing status storage (in production, use Redis or similar)
processing_status: Dict[str, ProcessingStatus] = {}


def ensure_ingredient_items(ingredients):
    """
    Convert ingredients to IngredientItem format if needed.
    Handles both string format and dict format, ensuring consistent output.
    
    Args:
        ingredients: List of ingredients (can be strings or dicts)
    
    Returns:
        List of dicts in format [{"name": "...", "count": ...}, ...]
    """
    result = []
    for ing in ingredients:
        if isinstance(ing, str):
            # Convert string to IngredientItem format
            result.append({"name": ing, "count": 1})
        elif isinstance(ing, dict):
            # Already in correct format, but ensure it has both fields
            if "name" in ing:
                result.append({
                    "name": ing["name"],
                    "count": ing.get("count", 1)
                })
        else:
            # Handle any other type by converting to string
            result.append({"name": str(ing), "count": 1})
    return result


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        message="RecipeAI API is running",
        timestamp=time.time()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="All systems operational",
        timestamp=time.time()
    )


@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image for processing
    Returns the file path for subsequent processing
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Generate unique filename
        timestamp = int(time.time() * 1000)
        file_extension = Path(file.filename).suffix
        filename = f"upload_{timestamp}{file_extension}"
        file_path = UPLOAD_DIR / filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return JSONResponse(content={
            "success": True,
            "file_path": str(file_path),
            "filename": filename,
            "message": "Image uploaded successfully"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/api/detect-ingredients", response_model=IngredientsResponse)
async def detect_ingredients(file_path: str):
    """
    Detect ingredients from an uploaded image
    Uses Qwen vision model with caching
    Returns ingredients list and labeled image URL
    """
    try:
        start_time = time.time()
        
        # Check if file exists
        if not Path(file_path).exists():
            raise HTTPException(status_code=404, detail="Image file not found")
        
        # Check cache first
        img_hash = get_image_hash(file_path)
        cache = load_cache()
        cache_hit = img_hash in cache
        
        # Extract ingredients (returns dict with ingredients and labeled_image_path)
        result = extract_ingredients(file_path)
        
        # Handle both old format (list) and new format (dict)
        if isinstance(result, dict):
            ingredients = result.get("ingredients", [])
            labeled_image_path = result.get("labeled_image_path")
        else:
            ingredients = result
            labeled_image_path = None
        
        # CRITICAL: Ensure ingredients are in correct format
        # Convert any strings to IngredientItem objects
        ingredients = ensure_ingredient_items(ingredients)
        
        # Convert labeled image path to URL
        labeled_image_url = None
        if labeled_image_path:
            labeled_filename = Path(labeled_image_path).name
            labeled_image_url = f"/uploads/{labeled_filename}"
        
        processing_time = time.time() - start_time
        
        return IngredientsResponse(
            ingredients=ingredients,
            processing_time=round(processing_time, 3),
            cache_hit=cache_hit,
            labeled_image_url=labeled_image_url
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingredient detection failed: {str(e)}")


@app.post("/api/match-recipes", response_model=RecipesResponse)
async def match_recipes(ingredients: List[Any], top_n: int = 20, dietary_preference: Optional[str] = None, sort_by: str = "match_percentage"):
    """
    Find best recipe matches for given ingredients
    Supports both simple string lists and quantity-aware ingredient objects
    Supports dietary filtering: 'vegetarian', 'non-vegetarian', or 'all'
    Supports dual sorting: 'match_percentage' (default) or 'ingredients_used'
    """
    try:
        start_time = time.time()
        
        if not ingredients:
            raise HTTPException(status_code=400, detail="No ingredients provided")
        
        # Validate sort_by parameter
        if sort_by not in ["match_percentage", "ingredients_used"]:
            raise HTTPException(status_code=400, detail="sort_by must be 'match_percentage' or 'ingredients_used'")
        
        # Extract ingredient names for validation
        detected_ingredient_names = set()
        for ingredient in ingredients:
            if isinstance(ingredient, dict):
                detected_ingredient_names.add(ingredient.get("name", "").lower().strip())
            elif isinstance(ingredient, str):
                detected_ingredient_names.add(ingredient.lower().strip())
            else:
                detected_ingredient_names.add(getattr(ingredient, "name", str(ingredient)).lower().strip())
        
        # Find matching recipes with dietary filter and sorting preference
        recipes = find_best_recipes(ingredients, top_n=top_n, dietary_preference=dietary_preference, sort_by=sort_by)
        
        # VALIDATION: Ensure matched ingredients are actually from detected ingredients
        # This prevents false positives from fuzzy matching
        for recipe in recipes:
            if "matched" in recipe and recipe["matched"]:
                # Validate each matched ingredient
                validated_matched = []
                for matched_ing in recipe["matched"]:
                    matched_ing_lower = matched_ing.lower().strip()
                    # Check if this matched ingredient corresponds to an actual detected ingredient
                    is_valid = False
                    for detected_ing in detected_ingredient_names:
                        # Allow exact match or if detected ingredient is in the matched ingredient name
                        if detected_ing == matched_ing_lower or (len(detected_ing) >= 4 and detected_ing in matched_ing_lower.split()):
                            is_valid = True
                            break
                    
                    if is_valid:
                        validated_matched.append(matched_ing)
                
                # Update with validated list
                recipe["matched"] = validated_matched
                
                # Recalculate score based on validated matches
                if len(recipe.get("ingredients", [])) > 0:
                    original_total = len(recipe["matched"]) + len(recipe.get("missing", []))
                    if original_total > 0:
                        recipe["score"] = round((len(validated_matched) / original_total) * 100, 2)
        
        processing_time = time.time() - start_time
        
        return RecipesResponse(
            recipes=[RecipeMatch(**recipe) for recipe in recipes],
            processing_time=round(processing_time, 3)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recipe matching failed: {str(e)}")


@app.post("/api/sustainability-analysis", response_model=SustainabilityResponse)
async def sustainability_analysis(user_ingredients: List[Any], recipe_data: Dict[str, Any]):
    """
    Generate comprehensive sustainability report for a recipe
    Supports both simple string lists and quantity-aware ingredient objects
    """
    try:
        start_time = time.time()
        
        # Convert ingredients to string list if they're objects
        ingredient_names = []
        for ingredient in user_ingredients:
            if isinstance(ingredient, dict):
                # New format: {"name": "apple", "count": 3}
                ingredient_names.append(ingredient.get("name", ""))
            elif isinstance(ingredient, str):
                # Old format: "apple"
                ingredient_names.append(ingredient)
            else:
                # Handle IngredientItem objects (Pydantic models)
                ingredient_names.append(getattr(ingredient, "name", str(ingredient)))
        
        # Filter out empty strings
        ingredient_names = [name for name in ingredient_names if name]
        
        # Generate sustainability report
        report = generate_full_sustainability_report(ingredient_names, recipe_data)
        
        processing_time = time.time() - start_time
        
        return SustainabilityResponse(
            report=report,
            processing_time=round(processing_time, 3)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sustainability analysis failed: {str(e)}")


@app.post("/api/ai-recommendation", response_model=RecommendationResponse)
async def ai_recommendation(ingredients: List[Any], recipes: List[str], top_recipe: Optional[Dict[str, Any]] = None):
    """
    Get AI-powered recipe recommendation from Granite
    Supports both simple string lists and quantity-aware ingredient objects
    """
    try:
        start_time = time.time()
        
        # Convert ingredients to string list if they're objects
        ingredient_names = []
        for ingredient in ingredients:
            if isinstance(ingredient, dict):
                # New format: {"name": "apple", "count": 3}
                ingredient_names.append(ingredient.get("name", ""))
            elif isinstance(ingredient, str):
                # Old format: "apple"
                ingredient_names.append(ingredient)
            else:
                # Handle IngredientItem objects (Pydantic models)
                ingredient_names.append(getattr(ingredient, "name", str(ingredient)))
        
        # Filter out empty strings
        ingredient_names = [name for name in ingredient_names if name]
        
        # Get recommendation from Granite
        recommendation = get_recommendation(ingredient_names, recipes, top_recipe)
        
        processing_time = time.time() - start_time
        
        return RecommendationResponse(
            recommendation=recommendation,
            processing_time=round(processing_time, 3)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI recommendation failed: {str(e)}")


@app.post("/api/analysis-stream")
async def analysis_stream(file_path: str, dietary_preference: Optional[str] = None, sort_by: str = "match_percentage"):
    """
    Stream end-to-end analysis progress and results via Server-Sent Events (SSE).
    """
    import asyncio
    from fastapi.responses import StreamingResponse

    async def event_generator():
        try:
            # Stage 1: Upload / Setup
            yield f"data: {json.dumps({'stage': 'upload', 'progress': 10, 'message': 'Image setup complete'})}\n\n"
            await asyncio.sleep(0.05)
            
            # Stage 2: Detect ingredients
            yield f"data: {json.dumps({'stage': 'detection', 'progress': 30, 'message': 'Detecting ingredients with AI...'})}\n\n"
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, extract_ingredients, file_path)
            
            if isinstance(result, dict):
                ingredients = result.get("ingredients", [])
                labeled_image_path = result.get("labeled_image_path")
            else:
                ingredients = result
                labeled_image_path = None
                
            ingredients = ensure_ingredient_items(ingredients)
            labeled_image_url = None
            if labeled_image_path:
                labeled_filename = Path(labeled_image_path).name
                labeled_image_url = f"/uploads/{labeled_filename}"
                
            yield f"data: {json.dumps({
                'stage': 'detection',
                'progress': 40,
                'message': f'Detected {len(ingredients)} ingredients',
                'data': {
                    'ingredients': ingredients,
                    'labeled_image_url': labeled_image_url
                }
            })}\n\n"
            
            if not ingredients:
                yield f"data: {json.dumps({'stage': 'error', 'progress': 0, 'message': 'No ingredients detected'})}\n\n"
                return
                
            # Stage 3: Match recipes
            yield f"data: {json.dumps({'stage': 'matching', 'progress': 50, 'message': 'Matching recipes...'})}\n\n"
            recipes = await loop.run_in_executor(
                None, 
                find_best_recipes, 
                ingredients, 20, dietary_preference, 0.3, sort_by
            )
            
            # Perform recipe matches validation
            detected_names = {ing["name"].lower().strip() for ing in ingredients}
            for recipe in recipes:
                if "matched" in recipe and recipe["matched"]:
                    validated_matched = []
                    for matched_ing in recipe["matched"]:
                        matched_ing_lower = matched_ing.lower().strip()
                        is_valid = False
                        for det in detected_names:
                            if det == matched_ing_lower or (len(det) >= 4 and det in matched_ing_lower.split()):
                                is_valid = True
                                break
                        if is_valid:
                            validated_matched.append(matched_ing)
                    recipe["matched"] = validated_matched
                    if len(recipe.get("ingredients", [])) > 0:
                        orig = len(recipe["matched"]) + len(recipe.get("missing", []))
                        if orig > 0:
                            recipe["score"] = round((len(validated_matched) / orig) * 100, 2)
            
            yield f"data: {json.dumps({
                'stage': 'matching',
                'progress': 60,
                'message': f'Found {len(recipes)} matching recipes',
                'data': {'recipes': recipes}
            })}\n\n"
            
            if not recipes:
                yield f"data: {json.dumps({'stage': 'error', 'progress': 0, 'message': 'No matching recipes found'})}\n\n"
                return
                
            top_recipe = recipes[0]
            
            # Stage 4: Sustainability analysis
            yield f"data: {json.dumps({'stage': 'sustainability', 'progress': 70, 'message': 'Calculating sustainability metrics...'})}\n\n"
            
            sustainability_report = await loop.run_in_executor(
                None, 
                generate_full_sustainability_report,
                [i["name"] for i in ingredients], 
                top_recipe
            )
            
            yield f"data: {json.dumps({
                'stage': 'sustainability',
                'progress': 80,
                'message': 'Sustainability metrics calculated',
                'data': {'sustainability': sustainability_report}
            })}\n\n"
            
            # Stage 5: Get AI Recommendations & tips
            yield f"data: {json.dumps({'stage': 'ai', 'progress': 90, 'message': 'Generating AI recommendations...'})}\n\n"
            
            recipe_names = [r["name"] for r in recipes[:5]]
            
            # Run Granite recommendation in background thread
            ai_recommendation = await loop.run_in_executor(
                None,
                get_recommendation,
                [i["name"] for i in ingredients],
                recipe_names,
                top_recipe
            )
            
            unused_ingredients = list(set(i["name"] for i in ingredients) - set(top_recipe.get("matched", [])))
            sustainability_tips = None
            if unused_ingredients:
                sustainability_tips = await loop.run_in_executor(
                    None,
                    generate_sustainability_tips,
                    unused_ingredients,
                    top_recipe.get("target", "General")
                )
                
            yield f"data: {json.dumps({
                'stage': 'ai',
                'progress': 95,
                'message': 'AI recommendations generated',
                'data': {
                    'ai_recommendation': ai_recommendation,
                    'sustainability_tips': sustainability_tips
                }
            })}\n\n"
            
            # Complete
            yield f"data: {json.dumps({
                'stage': 'complete',
                'progress': 100,
                'message': 'Analysis complete!',
                'data': {
                    'ingredients': ingredients,
                    'recipes': recipes,
                    'top_recipe': top_recipe,
                    'sustainability': sustainability_report,
                    'ai_recommendation': ai_recommendation,
                    'sustainability_tips': sustainability_tips,
                    'labeled_image_url': labeled_image_url
                }
            })}\n\n"
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'stage': 'error', 'progress': 0, 'message': f'Analysis failed: {str(e)}'})}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/chat")
async def chat_with_chef(req: ChatRequest):
    """
    Chat with the AI Chef (Granite) about cooking, recipes, or customizations.
    """
    try:
        import asyncio
        from granite import generate_with_granite, check_ollama_connection, check_model_available
        
        if not check_ollama_connection() or not check_model_available():
            return JSONResponse(content={
                "response": "Hello! I am your AI Chef, but my backend server (Ollama) is currently offline. Please check if Ollama is running."
            })
            
        # Build prompt with conversation history and context
        context_prompt = f"""You are a sustainable cooking assistant and professional chef powered by IBM Granite AI.
The user has these available ingredients: {', '.join(req.ingredients)}
"""
        if req.current_recipe:
            context_prompt += f"They are currently looking at or cooking the recipe: {req.current_recipe}\n"
            
        context_prompt += "\nHere is the conversation history so far:\n"
        for msg in req.history:
            role_name = "User" if msg.get("role") == "user" else "Chef"
            context_prompt += f"{role_name}: {msg.get('content')}\n"
            
        context_prompt += f"\nUser's new message: {req.message}\n"
        context_prompt += "\nChef response (be helpful, friendly, and focus on sustainability and waste reduction):"
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            generate_with_granite,
            context_prompt,
            0.6,  # slightly higher temperature for creative chatting
            300   # max tokens
        )
        
        if not response:
            response = "I'm sorry, I encountered an issue generating a response. Let's try again!"
            
        return JSONResponse(content={"response": response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.post("/api/full-analysis", response_model=FullAnalysisResponse)
async def full_analysis(file_path: str, dietary_preference: Optional[str] = None):
    """
    Complete end-to-end analysis pipeline
    1. Detect ingredients from image
    2. Match recipes (with optional dietary filtering)
    3. Generate sustainability report
    4. Get AI recommendations
    5. Generate SDG analysis
    
    dietary_preference: 'vegetarian', 'non-vegetarian', or 'all'
    """
    try:
        total_start = time.time()
        stages = {}
        
        # Stage 1: Detect ingredients
        stage_start = time.time()
        result = extract_ingredients(file_path)
        stages["ingredient_detection"] = round(time.time() - stage_start, 3)
        
        # Handle both old format (list) and new format (dict)
        if isinstance(result, dict):
            ingredients = result.get("ingredients", [])
        else:
            ingredients = result
        
        if not ingredients:
            raise HTTPException(status_code=400, detail="No ingredients detected in image")
        
        # Stage 2: Match recipes with dietary filter
        stage_start = time.time()
        recipes = find_best_recipes(ingredients, top_n=20, dietary_preference=dietary_preference)
        stages["recipe_matching"] = round(time.time() - stage_start, 3)
        
        if not recipes:
            raise HTTPException(status_code=404, detail="No matching recipes found")
        
        # Stage 3: Get recommendations with analysis
        stage_start = time.time()
        recommendation_data = get_recipe_recommendations_with_analysis(recipes, ingredients)
        top_recipe = recommendation_data.get("top_recommendation")
        stages["recommendation_analysis"] = round(time.time() - stage_start, 3)
        
        # Stage 4: Generate sustainability report
        stage_start = time.time()
        sustainability_report = None
        if top_recipe:
            sustainability_report = generate_full_sustainability_report(ingredients, top_recipe)
        stages["sustainability_analysis"] = round(time.time() - stage_start, 3)
        
        # Stage 5: Get AI recommendation from Granite
        stage_start = time.time()
        recipe_names = [r["name"] for r in recipes]
        ai_recommendation = get_recommendation(ingredients, recipe_names, top_recipe)
        stages["ai_recommendation"] = round(time.time() - stage_start, 3)
        
        # Stage 6: Generate SDG analysis
        stage_start = time.time()
        sdg_analysis = None
        if top_recipe and sustainability_report:
            waste_score = sustainability_report["waste_reduction"]["score"]
            co2_saved = sustainability_report["co2_impact"]["net_co2_saved"]
            sdg_analysis = generate_sdg_impact_analysis(
                top_recipe["name"],
                top_recipe.get("matched", []),
                waste_score,
                co2_saved
            )
        stages["sdg_analysis"] = round(time.time() - stage_start, 3)
        
        # Stage 7: Generate sustainability tips
        stage_start = time.time()
        sustainability_tips = None
        if top_recipe:
            unused_ingredients = list(set(ingredients) - set(top_recipe.get("matched", [])))
            if unused_ingredients:
                sustainability_tips = generate_sustainability_tips(
                    unused_ingredients,
                    top_recipe.get("target", "General")
                )
        stages["sustainability_tips"] = round(time.time() - stage_start, 3)
        
        total_time = time.time() - total_start
        
        return FullAnalysisResponse(
            ingredients=ingredients,
            recipes=recipes,
            top_recipe=top_recipe,
            sustainability_report=sustainability_report if sustainability_report is not None else {},
            ai_recommendation=ai_recommendation,
            sdg_analysis=sdg_analysis,
            sustainability_tips=sustainability_tips,
            total_processing_time=round(total_time, 3),
            stages=stages
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full analysis failed: {str(e)}")


@app.get("/api/sample-images")
async def get_sample_images():
    """
    Get list of available sample images
    """
    try:
        samples_dir = PROJECT_ROOT / "samples"
        if not samples_dir.exists():
            return JSONResponse(content={"samples": []})
        
        samples = []
        for file in samples_dir.iterdir():
            if file.is_file() and file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                samples.append({
                    "name": file.name,
                    "path": str(file)
                })
        
        return JSONResponse(content={"samples": samples})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sample images: {str(e)}")


@app.delete("/api/cleanup")
async def cleanup_uploads():
    """
    Clean up uploaded files (optional maintenance endpoint)
    """
    try:
        count = 0
        for file in UPLOAD_DIR.iterdir():
            if file.is_file():
                file.unlink()
                count += 1
        
        return JSONResponse(content={
            "success": True,
            "message": f"Cleaned up {count} files"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "detail": str(exc)}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    print("Starting RecipeAI FastAPI Backend...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

# Made with Bob
