# Technical Implementation Guide
## AI-Powered Food Waste Reduction Assistant

**Version:** 1.0  
**Last Updated:** June 19, 2026  
**Target Audience:** Developers, Technical Contributors

---

## Table of Contents

1. [System Architecture Overview](#1-system-architecture-overview)
2. [Technology Stack](#2-technology-stack)
3. [Component Deep Dive](#3-component-deep-dive)
4. [IBM Granite Integration](#4-ibm-granite-integration)
5. [Vision AI Implementation](#5-vision-ai-implementation)
6. [Recipe Matching System](#6-recipe-matching-system)
7. [Caching & Performance](#7-caching--performance)
8. [Data Models & Schema](#8-data-models--schema)
9. [Code Organization](#9-code-organization)
10. [Testing Strategy](#10-testing-strategy)
11. [Error Handling & Logging](#11-error-handling--logging)
12. [Security Considerations](#12-security-considerations)

---

## 1. System Architecture Overview

### 1.1 Three-Layer AI Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 1: Vision AI                        │
│              (Qwen2.5-VL-3B-Instruct Model)                 │
│  Input: Fridge/Pantry Image                                 │
│  Output: List of detected ingredients                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 LAYER 2: Recipe Matcher                      │
│              (Local Algorithm-Based Matching)                │
│  Input: Ingredient list + Recipe database                   │
│  Output: Top 5 matching recipes with scores                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              LAYER 3: Intelligence Layer                     │
│                (IBM Granite 3.0 8B Instruct)                │
│  Input: Ingredients + Recipe candidates                     │
│  Output: Best recipe + sustainability reasoning             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Design Principles

1. **Modularity:** Each layer is independent and testable
2. **Performance First:** Caching at every level
3. **Local-First:** Vision processing happens locally (no API calls)
4. **Sustainability Focus:** Every decision optimized for waste reduction
5. **Scalability:** Architecture supports future enhancements

### 1.3 Data Flow

```
Image → Hash → Cache Check → [Hit: Return Cached] 
                           ↓
                    [Miss: Process]
                           ↓
              Load Vision Model (Lazy)
                           ↓
              Model Inference (GPU)
                           ↓
              Parse & Normalize
                           ↓
              Save to Cache
                           ↓
              Recipe Matching
                           ↓
              IBM Granite API
                           ↓
              Final Recommendation
```

---

## 2. Technology Stack

### 2.1 Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.8+ | Primary development |
| **Deep Learning** | PyTorch | 2.0+ | Neural network framework |
| **Transformers** | Hugging Face | 4.30+ | Model loading & inference |
| **Vision Model** | Qwen2.5-VL-3B | Latest | Ingredient detection |
| **LLM** | IBM Granite 3.0 | 8B Instruct | Recipe reasoning |
| **GPU** | CUDA | 11.8+ | Fast inference |

### 2.2 Dependencies

```txt
torch>=2.0.0
transformers>=4.30.0
qwen-vl-utils>=0.1.0
ibm-watsonx-ai>=0.2.0
pillow>=9.0.0
numpy>=1.24.0
```

### 2.3 Hardware Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8GB
- GPU: NVIDIA GTX 1060 (6GB VRAM)
- Storage: 10GB

**Recommended:**
- CPU: 8 cores
- RAM: 16GB
- GPU: NVIDIA RTX 3060 (12GB VRAM)
- Storage: 20GB SSD

---

## 3. Component Deep Dive

### 3.1 Vision Component (`vision.py`)

#### Key Features
- **Lazy Model Loading:** Model loads only on cache miss
- **Image Hashing:** MD5 hash for cache keys
- **Persistent Caching:** JSON-based cache file
- **Normalization:** Standardize ingredient names

#### Implementation

```python
# Lazy loading pattern
model = None
processor = None

def init_model():
    global model, processor
    if model is None:
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16,  # Half precision
            device_map="cuda"            # GPU acceleration
        )
        processor = AutoProcessor.from_pretrained(MODEL_NAME)
```

#### Prompt Engineering

```python
prompt = """
Identify only edible food items.
Return a simple comma-separated list.
Maximum 15 ingredients.
Do not explain. Do not use JSON.

Example:
tomato, onion, milk, bread
"""
```

**Design Rationale:**
- Simple format for easy parsing
- Limit to 15 prevents overwhelming
- Example-driven improves accuracy

#### Normalization

```python
NORMALIZATION = {
    "tomatoes": "tomato",
    "onions": "onion",
    "bell peppers": "capsicum"
}
```

### 3.2 Recipe Matcher (`recipe_matcher.py`)

#### Algorithm

```python
def find_best_recipes(user_ingredients, top_n=5):
    user_set = set(x.lower() for x in user_ingredients)
    
    for recipe in RECIPES:
        recipe_set = set(x.lower() for x in recipe["ingredients"])
        matched = user_set & recipe_set
        score = len(matched) / len(recipe_set) * 100
```

#### Scoring Formula

```
Score = (Matched Ingredients / Total Recipe Ingredients) × 100
```

**Example:**
- User has: `[rice, curd, lemon]`
- Recipe needs: `[rice, curd]`
- Score: `2/2 × 100 = 100%`

### 3.3 Intelligence Layer (`granite.py`)

#### IBM Granite Configuration

```python
credentials = {
    "url": "https://us-south.ml.cloud.ibm.com",
    "apikey": API_KEY
}

model = ModelInference(
    model_id="ibm/granite-3-8b-instruct",
    credentials=credentials,
    project_id=PROJECT_ID
)
```

#### Generation Parameters

```python
params = {
    "max_new_tokens": 400,      # Detailed response
    "temperature": 0.2,          # Low = deterministic
    "decoding_method": "greedy"  # Highest probability
}
```

---

## 4. IBM Granite Integration

### 4.1 Model Selection

**Chosen:** `ibm/granite-3-8b-instruct`

**Rationale:**
- 8B parameters - balance of capability and speed
- Instruction-tuned for structured prompts
- Sustainability knowledge
- API availability via Watsonx.ai

### 4.2 Prompt Structure

```python
prompt = f"""
You are a sustainable cooking assistant powered by IBM Granite.
Available ingredients:
{json.dumps(ingredients)}

Recipe candidates:
{json.dumps(recipes, indent=2)}

Choose the best recipe that maximizes ingredients and reduces waste.
Return:
Recipe Name: <name>
Reason: <explanation>
Missing Ingredients: <list or 'None'>
Waste Reduction Score: <1-10 with justification>
Cooking Instructions: <numbered steps>
"""
```

### 4.3 Local Deployment Alternative

For **offline deployment** without API:

```python
# Using Ollama for local inference
from ollama import Client

client = Client(host='http://localhost:11434')

def get_recommendation_local(ingredients, recipes):
    response = client.generate(
        model='granite:8b',
        prompt=prompt
    )
    return response['response']
```

**Benefits:**
- No API costs
- Complete privacy
- No internet required

**Requirements:**
- 16GB+ RAM
- 4-5GB model download

---

## 5. Vision AI Implementation

### 5.1 Model Architecture

**Qwen2.5-VL-3B-Instruct:**
- 3 billion parameters
- Vision encoder + Language decoder
- Instruction-tuned

### 5.2 Processing Pipeline

```python
# 1. Create message with image
messages = [{
    "role": "user",
    "content": [
        {"type": "image", "image": image_path},
        {"type": "text", "text": prompt}
    ]
}]

# 2. Apply chat template
text = processor.apply_chat_template(messages, tokenize=False)

# 3. Process vision info
image_inputs, _ = process_vision_info(messages)

# 4. Tokenize
inputs = processor(text=[text], images=image_inputs, return_tensors="pt")

# 5. Move to GPU
inputs = inputs.to(model.device)

# 6. Generate
generated_ids = model.generate(**inputs, max_new_tokens=40)
```

### 5.3 GPU Memory Management

```python
# Check memory usage
print(torch.cuda.memory_allocated() / 1024**3, "GB allocated")

# Clear cache if needed
torch.cuda.empty_cache()
```

**Optimization:**
- Use `torch.float16` (half precision)
- Batch size = 1
- Clear cache between runs

### 5.4 Performance Benchmarks

| Operation | First Run | Cached | Speedup |
|-----------|-----------|--------|---------|
| Model Loading | 4.5s | 0s | ∞ |
| Inference | 2.2s | 0s | ∞ |
| Total | 7.5s | 0.02s | 375x |

---

## 6. Recipe Matching System

### 6.1 Database Schema

```json
{
  "name": "Curd Rice",
  "ingredients": ["rice", "curd"],
  "target": "leftover rice",
  "cuisine": "Indian",
  "difficulty": "Easy",
  "time": "15 minutes",
  "servings": 2
}
```

### 6.2 Set Operations

```python
# Example
user = {"rice", "curd", "lemon"}
recipe = {"rice", "curd"}

# Matched ingredients
matched = user & recipe  # {"rice", "curd"}

# Missing ingredients
missing = recipe - user  # set()

# Score
score = len(matched) / len(recipe) * 100  # 100%
```

### 6.3 Adding Recipes

```python
# recipes.json
{
  "name": "Paneer Tikka",
  "ingredients": ["paneer", "capsicum", "onion", "curd"],
  "target": "leftover paneer",
  "cuisine": "Indian",
  "difficulty": "Medium",
  "time": "30 minutes",
  "servings": 4
}
```

**Best Practices:**
- Use lowercase
- Simple names (no adjectives)
- Canonical forms (tomato, not tomatoes)

---

## 7. Caching & Performance

### 7.1 Cache Architecture

```json
{
  "abc123...": ["tomato", "onion"],
  "def456...": ["rice", "curd"]
}
```

### 7.2 Hash Generation

```python
def get_image_hash(path):
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
```

**Why MD5?**
- Fast computation
- Sufficient for cache keys
- Consistent across runs

### 7.3 Cache Operations

```python
# Check cache
img_hash = get_image_hash(image_path)
cache = load_cache()

if img_hash in cache:
    return cache[img_hash]  # Hit
else:
    ingredients = process_image(image_path)
    cache[img_hash] = ingredients
    save_cache(cache)
    return ingredients
```

### 7.4 Performance Metrics

**Expected Cache Hit Rate:**
- First-time users: 0%
- Repeat users: 80-90%
- Overall: 60-70%

---

## 8. Data Models & Schema

### 8.1 Ingredient Model

```python
from typing import List

class Ingredient:
    def __init__(self, name: str, confidence: float = 1.0):
        self.name = name.lower().strip()
        self.confidence = confidence
        self.normalized_name = self._normalize()
    
    def _normalize(self) -> str:
        return NORMALIZATION.get(self.name, self.name)
```

### 8.2 Recipe Model

```python
from dataclasses import dataclass

@dataclass
class Recipe:
    name: str
    ingredients: List[str]
    target: str
    cuisine: str = "Indian"
    difficulty: str = "Easy"
    time: str = "30 minutes"
    servings: int = 2
    
    def match_score(self, user_ingredients: List[str]) -> float:
        user_set = set(i.lower() for i in user_ingredients)
        recipe_set = set(i.lower() for i in self.ingredients)
        matched = user_set & recipe_set
        return len(matched) / len(recipe_set) * 100
```

### 8.3 Recommendation Model

```python
@dataclass
class Recommendation:
    recipe_name: str
    reason: str
    missing_ingredients: List[str]
    waste_reduction_score: int  # 1-10
    cooking_instructions: List[str]
    sustainability_impact: str
```

---

## 9. Code Organization

### 9.1 Project Structure

```
RecipeAI/
├── vision.py              # Vision AI component
├── granite.py             # IBM Granite integration
├── recipe_matcher.py      # Recipe matching
├── recipes.json           # Recipe database
├── ingredient_cache.json  # Cache file
├── samples/               # Sample images
│   ├── fridge_1.jpeg
│   └── fridge_2.png
├── docs/                  # Documentation
│   ├── PROJECT_CONCEPT.md
│   ├── TECHNICAL_GUIDE.md
│   ├── SETUP_INSTRUCTIONS.md
│   ├── SUSTAINABILITY_METRICS.md
│   └── AI_ARCHITECTURE.md
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### 9.2 Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `vision.py` | Image processing, ingredient extraction |
| `granite.py` | LLM reasoning, recommendations |
| `recipe_matcher.py` | Recipe scoring, matching |
| `recipes.json` | Recipe database |

### 9.3 Configuration Management

```python
# config.py (future enhancement)
import os

class Config:
    # Models
    VISION_MODEL = "Qwen/Qwen2.5-VL-3B-Instruct"
    GRANITE_MODEL = "ibm/granite-3-8b-instruct"
    
    # API
    IBM_API_KEY = os.getenv("IBM_API_KEY")
    IBM_PROJECT_ID = os.getenv("IBM_PROJECT_ID")
    
    # Cache
    CACHE_FILE = "ingredient_cache.json"
    CACHE_MAX_AGE_DAYS = 30
    
    # Performance
    MAX_NEW_TOKENS_VISION = 40
    MAX_NEW_TOKENS_GRANITE = 400
    TEMPERATURE = 0.2
    TOP_N_RECIPES = 5
```

---

## 10. Testing Strategy

### 10.1 Unit Tests

```python
# tests/test_vision.py
import unittest
from vision import extract_ingredients, get_image_hash

class TestVision(unittest.TestCase):
    def test_hash_consistency(self):
        hash1 = get_image_hash("samples/fridge_1.jpeg")
        hash2 = get_image_hash("samples/fridge_1.jpeg")
        self.assertEqual(hash1, hash2)
    
    def test_extraction(self):
        ingredients = extract_ingredients("samples/fridge_2.png")
        self.assertIsInstance(ingredients, list)
        self.assertGreater(len(ingredients), 0)
```

```python
# tests/test_recipe_matcher.py
import unittest
from recipe_matcher import find_best_recipes

class TestMatcher(unittest.TestCase):
    def test_perfect_match(self):
        ingredients = ["rice", "curd"]
        recipes = find_best_recipes(ingredients, top_n=1)
        self.assertEqual(recipes[0]["name"], "Curd Rice")
        self.assertEqual(recipes[0]["score"], 100.0)
```

### 10.2 Integration Tests

```python
# tests/test_integration.py
def test_full_pipeline():
    # Extract ingredients
    ingredients = extract_ingredients("samples/fridge_2.png")
    
    # Match recipes
    recipes = find_best_recipes(ingredients, top_n=5)
    
    # Get recommendation
    recipe_names = [r["name"] for r in recipes]
    recommendation = get_recommendation(ingredients, recipe_names)
    
    assert isinstance(recommendation, str)
    assert len(recommendation) > 0
```

### 10.3 Performance Tests

```python
def test_cache_speedup():
    # First run (cache miss)
    start = time.time()
    ingredients1 = extract_ingredients("samples/fridge_1.jpeg")
    time1 = time.time() - start
    
    # Second run (cache hit)
    start = time.time()
    ingredients2 = extract_ingredients("samples/fridge_1.jpeg")
    time2 = time.time() - start
    
    # Cache should be 10x+ faster
    assert time2 < time1 / 10
    assert ingredients1 == ingredients2
```

### 10.4 Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=. tests/

# Run specific test
python -m pytest tests/test_vision.py -v
```

---

## 11. Error Handling & Logging

### 11.1 Exception Hierarchy

```python
class RecipeAIException(Exception):
    """Base exception."""
    pass

class VisionException(RecipeAIException):
    """Vision processing errors."""
    pass

class RecipeMatchException(RecipeAIException):
    """Recipe matching errors."""
    pass

class GraniteAPIException(RecipeAIException):
    """IBM Granite API errors."""
    pass
```

### 11.2 Graceful Degradation

```python
def extract_ingredients_safe(image_path: str):
    try:
        return extract_ingredients(image_path)
    except VisionException as e:
        print(f"Vision error: {e}")
        return prompt_user_for_ingredients()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def get_recommendation_safe(ingredients, recipes):
    try:
        return get_recommendation(ingredients, recipes)
    except GraniteAPIException as e:
        print(f"API error: {e}")
        return generate_local_recommendation(ingredients, recipes)
```

### 11.3 Retry Logic

```python
def retry(max_attempts=3, delay=1.0):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait = delay * (2 ** attempt)
                    print(f"Retry in {wait}s...")
                    time.sleep(wait)
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2.0)
def get_recommendation(ingredients, recipes):
    return model.generate_text(prompt=prompt)
```

### 11.4 Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('recipeai.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usage
logger.info(f"Processing image: {image_path}")
logger.error(f"Error: {e}", exc_info=True)
```

---

## 12. Security Considerations

### 12.1 API Key Management

```python
# ❌ BAD: Hardcoded
API_KEY = "abc123"

# ✅ GOOD: Environment variables
import os
API_KEY = os.getenv("IBM_API_KEY")

# ✅ BETTER: .env file
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("IBM_API_KEY")
```

**.env file:**
```
IBM_API_KEY=your_key_here
IBM_PROJECT_ID=your_project_id
```

**.gitignore:**
```
.env
*.env
ingredient_cache.json
__pycache__/
```

### 12.2 Input Validation

```python
def validate_image(image_path: str) -> bool:
    # Check exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Check size (max 10MB)
    if os.path.getsize(image_path) > 10 * 1024 * 1024:
        raise ValueError("Image too large (max 10MB)")
    
    # Check extension
    valid = ['.jpg', '.jpeg', '.png', '.webp']
    ext = os.path.splitext(image_path)[1].lower()
    if ext not in valid:
        raise ValueError(f"Invalid format: {ext}")
    
    return True
```

### 12.3 Data Privacy

**Principles:**
1. Local vision processing (no image uploads)
2. Only ingredient lists sent to API
3. No user tracking
4. User-controlled cache

**Architecture:**
```
User Image → Local Vision AI → Ingredient List → API
                                      ↓
                              (No image sent)
```

### 12.4 Rate Limiting

```python
def rate_limit(max_calls: int, period: int):
    calls = []
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            now = time.time()
            calls[:] = [c for c in calls if now - c < period]
            
            if len(calls) >= max_calls:
                raise Exception(f"Rate limit: {max_calls}/{period}s")
            
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_calls=10, period=60)
def get_recommendation(ingredients, recipes):
    pass
```

---

## Appendix A: Performance Optimization

### A.1 Model Quantization

```python
# INT8 quantization (4x smaller)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    load_in_8bit=True,
    device_map="auto"
)
```

### A.2 Batch Processing

```python
def extract_ingredients_batch(image_paths: List[str]):
    results = []
    uncached = []
    
    # Check cache first
    for path in image_paths:
        img_hash = get_image_hash(path)
        if img_hash in cache:
            results.append(cache[img_hash])
        else:
            uncached.append(path)
    
    # Batch process uncached
    if uncached:
        batch_results = process_batch(uncached)
        results.extend(batch_results)
    
    return results
```

### A.3 Async Processing

```python
import asyncio

async def process_async(image_path: str):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        ingredients = await loop.run_in_executor(
            executor,
            extract_ingredients,
            image_path
        )
    return ingredients
```

---

## Appendix B: Deployment Options

### B.1 Docker Deployment

```dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04

RUN apt-get update && apt-get install -y python3.8 python3-pip

WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "vision.py"]
```

### B.2 Cloud Deployment

**AWS EC2 with GPU:**
- Instance: g4dn.xlarge (T4 GPU)
- OS: Ubuntu 20.04
- Storage: 50GB EBS

**Azure:**
- Instance: NC6 (K80 GPU)
- OS: Ubuntu 20.04

**GCP:**
- Instance: n1-standard-4 + T4 GPU
- OS: Ubuntu 20.04

---

## Appendix C: Monitoring

### C.1 Health Check

```python
def health_check():
    return {
        "status": "healthy",
        "vision_model": "loaded" if model else "not_loaded",
        "gpu": "available" if torch.cuda.is_available() else "unavailable",
        "cache_entries": len(load_cache())
    }
```

### C.2 Performance Metrics

```python
@dataclass
class Metrics:
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_response_time: float = 0.0
    
    def hit_rate(self):
        return self.cache_hits / self.total_requests * 100
```

---

**Document Version:** 1.0  
**Last Updated:** June 19, 2026  
**Maintained By:** RecipeAI Team

For setup instructions, see [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)  
For architecture diagrams, see [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)  
For sustainability metrics, see [SUSTAINABILITY_METRICS.md](SUSTAINABILITY_METRICS.md)