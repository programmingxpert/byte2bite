import hashlib
import json
import os
import time
import base64
import requests
from pathlib import Path
from recipe_matcher import find_best_recipes
from granite import get_recommendation
from PIL import Image, ImageDraw, ImageFont
import math

try:
    from backend.config import MODEL_MODE, TUNNEL_LOCAL_PORT, CLOUD_QWEN_MODEL
except ImportError:
    from config import MODEL_MODE, TUNNEL_LOCAL_PORT, CLOUD_QWEN_MODEL

# Conditional imports for local ML models
if MODEL_MODE == "local":
    import torch
    from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
    from qwen_vl_utils import process_vision_info


# Get the directory where this script is located (use /tmp on Vercel since filesystem is read-only)
SCRIPT_DIR = Path(__file__).parent
if os.getenv("VERCEL"):
    CACHE_FILE = Path("/tmp/ingredient_cache.json")
else:
    CACHE_FILE = SCRIPT_DIR / "ingredient_cache.json"
MODEL_NAME = "Qwen/Qwen2.5-VL-3B-Instruct"

# --- Cache Management Functions ---
def get_image_hash(path):
    """Generates an MD5 hash of the image file to use as a cache key."""
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        # Read in chunks to efficiently handle any file size safely
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def load_cache():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache_data):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache_data, f, indent=2)

# --- Model Loading Logic ---
# Global model variables initialized as None so we only load them if we hit a cache miss
model = None
processor = None

def init_model():
    global model, processor
    if model is None or processor is None:
        print("\n[Cache Miss] Loading Qwen Model into VRAM...")
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16,
            device_map="cuda"
        )
        processor = AutoProcessor.from_pretrained(MODEL_NAME)
        print("Model loaded successfully!")
        
        # Verify models loaded successfully
        if model is None:
            raise RuntimeError("Failed to load Qwen2.5-VL model")
        if processor is None:
            raise RuntimeError("Failed to load Qwen2.5-VL processor")

# Normalization Dictionary for canonical naming
NORMALIZATION = {
    "tomatoes": "tomato",
    "onions": "onion",
    "cucumbers": "cucumber",
    "carrots": "carrot",
    "potatoes": "potato",
    "bell peppers": "capsicum"
}

def create_labeled_image(image_path, ingredients):
    """
    Create a labeled version of the image with detected ingredients annotated.
    
    Args:
        image_path: Path to the original image
        ingredients: List of detected ingredients with counts [{"name": "apple", "count": 3}, ...]
    
    Returns:
        Path to the labeled image, or None if labeling fails
    """
    try:
        # Load the image
        img = Image.open(image_path)
        
        # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Create a copy to draw on
        labeled_img = img.copy()
        draw = ImageDraw.Draw(labeled_img)
        
        # Get image dimensions
        img_width, img_height = img.size
        
        # Try to load a nice font, fall back to default if not available
        # Try different font sizes based on image size
        font_size = max(20, min(40, img_height // 25))
        try:
            # Try to use a system font
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                # Try alternative font names
                font = ImageFont.truetype("Arial.ttf", font_size)
            except:
                # Fall back to default font
                font = ImageFont.load_default()
        
        # Color palette for labels (vibrant colors that stand out)
        colors = [
            (255, 87, 51),   # Red-Orange
            (46, 213, 115),  # Green
            (255, 195, 18),  # Yellow
            (52, 152, 219),  # Blue
            (155, 89, 182),  # Purple
            (241, 196, 15),  # Gold
            (26, 188, 156),  # Turquoise
            (230, 126, 34),  # Orange
        ]
        
        if not ingredients:
            # No ingredients detected - add a message
            text = "No ingredients detected"
            # Calculate text position (center of image)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (img_width - text_width) // 2
            y = (img_height - text_height) // 2
            
            # Draw background rectangle
            padding = 20
            draw.rectangle(
                [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
                fill=(0, 0, 0, 180)
            )
            draw.text((x, y), text, fill=(255, 255, 255), font=font)
        else:
            # Calculate grid layout for labels
            num_ingredients = len(ingredients)
            cols = min(3, num_ingredients)  # Max 3 columns
            rows = math.ceil(num_ingredients / cols)
            
            # Calculate spacing
            margin = 30
            label_spacing_x = (img_width - 2 * margin) // cols
            label_spacing_y = (img_height - 2 * margin) // rows
            
            # Draw each ingredient label
            for idx, ingredient in enumerate(ingredients):
                # Calculate position in grid
                col = idx % cols
                row = idx // cols
                
                # Calculate label position
                x = margin + col * label_spacing_x + label_spacing_x // 2
                y = margin + row * label_spacing_y + label_spacing_y // 2
                
                # Create label text
                name = ingredient["name"].capitalize()
                count = ingredient["count"]
                if count > 1:
                    label_text = f"{name} ×{count}"
                else:
                    label_text = name
                
                # Get color for this ingredient
                color = colors[idx % len(colors)]
                
                # Calculate text size
                bbox = draw.textbbox((0, 0), label_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Draw background rectangle with some padding
                padding = 15
                rect_x1 = x - text_width // 2 - padding
                rect_y1 = y - text_height // 2 - padding
                rect_x2 = x + text_width // 2 + padding
                rect_y2 = y + text_height // 2 + padding
                
                # Ensure rectangle stays within image bounds
                rect_x1 = max(5, rect_x1)
                rect_y1 = max(5, rect_y1)
                rect_x2 = min(img_width - 5, rect_x2)
                rect_y2 = min(img_height - 5, rect_y2)
                
                # Draw semi-transparent background
                draw.rectangle(
                    [rect_x1, rect_y1, rect_x2, rect_y2],
                    fill=color,
                    outline=(255, 255, 255),
                    width=3
                )
                
                # Draw text centered in rectangle
                text_x = (rect_x1 + rect_x2) // 2 - text_width // 2
                text_y = (rect_y1 + rect_y2) // 2 - text_height // 2
                draw.text((text_x, text_y), label_text, fill=(255, 255, 255), font=font)
                
                # Draw a small circle indicator at the position
                circle_radius = 8
                draw.ellipse(
                    [x - circle_radius, y - circle_radius, x + circle_radius, y + circle_radius],
                    fill=(255, 255, 255),
                    outline=color,
                    width=3
                )
        
        # Add a watermark/title at the top
        title = f"Detected: {len(ingredients)} ingredient{'s' if len(ingredients) != 1 else ''}"
        title_bbox = draw.textbbox((0, 0), title, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        title_height = title_bbox[3] - title_bbox[1]
        title_x = (img_width - title_width) // 2
        title_y = 15
        
        # Draw title background
        draw.rectangle(
            [title_x - 15, title_y - 10, title_x + title_width + 15, title_y + title_height + 10],
            fill=(0, 0, 0, 200)
        )
        draw.text((title_x, title_y), title, fill=(255, 255, 255), font=font)
        
        # Generate labeled image path
        path_obj = Path(image_path)
        labeled_path = path_obj.parent / f"{path_obj.stem}_labeled{path_obj.suffix}"
        
        # Save the labeled image
        labeled_img.save(labeled_path, quality=95)
        
        print(f"[SUCCESS] Labeled image created: {labeled_path}")
        return str(labeled_path)
        
    except Exception as e:
        print(f"[ERROR] Error creating labeled image: {e}")
        return None

def extract_ingredients(image_path):
    total_start = time.time()
    print("1. Starting extraction process")
    
    # Check cache first
    img_hash = get_image_hash(image_path)
    cache = load_cache()
    
    if img_hash in cache:
        print(f"\n[CACHE HIT] Found image match ({img_hash})!")
        print(f"--- Total pipeline extraction time: {time.time() - total_start:.4f}s ---")
        cached_data = cache[img_hash]
        
        # Handle both old format (list) and new format (dict)
        if isinstance(cached_data, list):
            # Old format - convert strings to IngredientItem objects
            print("[INFO] Converting old cache format (strings) to new format (objects)")
            ingredients = []
            for item in cached_data:
                if isinstance(item, str):
                    # Convert string to IngredientItem format
                    ingredients.append({"name": item, "count": 1})
                elif isinstance(item, dict):
                    # Already in correct format
                    ingredients.append(item)
            
            # Create labeled image
            labeled_path = create_labeled_image(image_path, ingredients)
            
            # Update cache with new format
            cache_entry = {
                "ingredients": ingredients,
                "labeled_image_path": labeled_path
            }
            cache[img_hash] = cache_entry
            save_cache(cache)
            print("[INFO] Cache updated to new format.")
            
            return {"ingredients": ingredients, "labeled_image_path": labeled_path}
        else:
            # New format - return as is
            return cached_data
        
    print(f"\n[CACHE MISS] Processing new image ({img_hash})...")
    
    result = ""
    if MODEL_MODE in ["cloud", "cloud_direct"]:
        print(f"[Cloud Mode] Calling remote Ollama ({CLOUD_QWEN_MODEL})...")
        try:
            import io
            with Image.open(image_path) as img:
                fmt = img.format if img.format else "JPEG"
                max_size = 512
                if img.width > max_size or img.height > max_size:
                    img.thumbnail((max_size, max_size))
                buffer = io.BytesIO()
                img.save(buffer, format=fmt)
                img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            
            port = TUNNEL_LOCAL_PORT if MODEL_MODE == "cloud" else 11434
            url = f"http://localhost:{port}/api/generate"
            if "moondream" in CLOUD_QWEN_MODEL.lower():
                prompt = "Identify all the food items visible in this image. Output them as a simple comma-separated list of ingredients. Example: milk, tomato, bread, cheese, onion."
            else:
                prompt = """Identify only edible food items with their quantities.
For each item, specify the count if multiple are visible.
Return in format: ingredient:count, ingredient:count
If only one item, use count of 1.
Maximum 15 ingredients.
Do not explain. Do not use JSON.

Example:
apple:3, tomato:2, milk:1, bread:1, onion:4"""
            
            payload = {
                "model": CLOUD_QWEN_MODEL,
                "prompt": prompt,
                "images": [img_base64],
                "stream": False
            }
            
            start_gen = time.time()
            response = requests.post(url, json=payload, timeout=300)
            if response.status_code == 200:
                result = response.json().get("response", "").strip()
                print(f"[Cloud Mode] Remote generation finished in {time.time() - start_gen:.4f}s")
            else:
                raise RuntimeError(f"Cloud Ollama returned status {response.status_code}: {response.text}")
        except Exception as e:
            print(f"[Cloud Mode Error] remote inference failed: {e}")
            raise e
    else:
        # Local Mode
        # Initialize the model now that we know we actually need it
        init_model()
        
        # Type guard: Ensure model and processor are loaded
        if model is None or processor is None:
            raise RuntimeError("Model or processor failed to initialize")
        
        prompt = """
Identify only edible food items with their quantities.
For each item, specify the count if multiple are visible.
Return in format: ingredient:count, ingredient:count
If only one item, use count of 1.
Maximum 15 ingredients.
Do not explain. Do not use JSON.

Example:
apple:3, tomato:2, milk:1, bread:1, onion:4
"""
        
        start = time.time()
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image", 
                        "image": image_path,
                        "max_pixels": 512 * 512  # Resize image to prevent VRAM OOM and speed up local run
                    },
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        print(f"2. Messages created ({time.time() - start:.4f}s)")
        
        start = time.time()
        text = processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        print(f"3. Chat template done ({time.time() - start:.4f}s)")
        
        start = time.time()
        vision_info = process_vision_info(messages)
        image_inputs = vision_info[0] if vision_info else None
        video_inputs = vision_info[1] if len(vision_info) > 1 else None
        print(f"4. Vision processing done ({time.time() - start:.4f}s)")
        
        start = time.time()
        inputs = processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt"
        )
        print(f"5. Processor done ({time.time() - start:.4f}s)")
        
        start = time.time()
        inputs = inputs.to(model.device)
        print(f"6. Moved to GPU ({time.time() - start:.4f}s)")
        
        print(torch.cuda.memory_allocated() / 1024**3, "GB allocated")
        print(torch.cuda.memory_reserved() / 1024**3, "GB reserved")
        
        print("7. Starting generation")
        start = time.time()
        # Type checker can't verify protocol compliance, but model has generate method
        generated_ids = model.generate(  # type: ignore[attr-defined]
            **inputs,
            max_new_tokens=40,
            do_sample=False,
            eos_token_id=processor.tokenizer.eos_token_id
        )
        generation_time = time.time() - start
        print(f"8. Generation finished ({generation_time:.4f}s)")
        
        start = time.time()
        generated_ids_trimmed = [
            out_ids[len(in_ids):]
            for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        
        result = processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]
    
    print(f"\nRAW RESPONSE FROM QWEN:\n{result}\n")
    
    try:
        raw_items = result.split(",")
        ingredients = []
        
        for item in raw_items:
            cleaned = item.strip().lower()
            if cleaned:
                # Parse quantity format: "ingredient:count" or just "ingredient"
                if ":" in cleaned:
                    parts = cleaned.split(":", 1)
                    ingredient_name = parts[0].strip()
                    try:
                        count = int(parts[1].strip())
                    except (ValueError, IndexError):
                        count = 1
                else:
                    ingredient_name = cleaned
                    count = 1
                
                # Normalize ingredient name
                normalized = NORMALIZATION.get(ingredient_name, ingredient_name)
                
                # Check if ingredient already exists and update count
                existing = next((ing for ing in ingredients if ing["name"] == normalized), None)
                if existing:
                    existing["count"] += count
                else:
                    ingredients.append({"name": normalized, "count": count})
        
        # Create labeled image
        labeled_image_path = create_labeled_image(image_path, ingredients)
        
        # Save results to the cache file (including labeled image path)
        cache_entry = {
            "ingredients": ingredients,
            "labeled_image_path": labeled_image_path
        }
        cache[img_hash] = cache_entry
        save_cache(cache)
        print("[INFO] New entry saved to local cache.")
        
        print(f"9. Post-processing done ({time.time() - start:.4f}s)")
        print(f"--- Total pipeline extraction time: {time.time() - total_start:.4f}s ---")
        return {"ingredients": ingredients, "labeled_image_path": labeled_image_path}
        
    except Exception as e:
        print("Parsing Error:", e)
        return []


# --- End-to-End Execution Flow ---
if __name__ == "__main__":
    # 1. Vision Layer: Get raw ingredients list
    sample_image = SCRIPT_DIR / "samples" / "fridge_2.png"
    result = extract_ingredients(str(sample_image))
    
    # Extract ingredients from result
    ingredients = result["ingredients"] if isinstance(result, dict) else result
    labeled_image_path = result.get("labeled_image_path") if isinstance(result, dict) else None

    print("\nDetected Ingredients:\n")
    print(ingredients)
    
    if labeled_image_path:
        print(f"\nLabeled image saved to: {labeled_image_path}")

    # 2. Matcher Layer: Score local datasets using ingredient intersection matrices
    recipes = find_best_recipes(ingredients, top_n=5)

    print("\nTop Recipe Matches:\n")
    for recipe in recipes:
        print(f"{recipe['name']} | {recipe['score']}%")

    # 3. Intelligence Layer: Fetch full sustainability breakdown from IBM Granite
    recipe_names = [recipe["name"] for recipe in recipes]

    print("\nFetching final reasoning breakdown from IBM Granite...")
    response = get_recommendation(ingredients, recipe_names)

    print("\nGranite Recommendation:\n")
    print(response)