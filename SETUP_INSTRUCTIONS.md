# Setup Instructions
## AI-Powered Food Waste Reduction Assistant

**Version:** 1.0  
**Last Updated:** June 19, 2026  
**Platform:** Windows 11 with PowerShell

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [System Requirements Check](#2-system-requirements-check)
3. [Python Environment Setup](#3-python-environment-setup)
4. [Installing Dependencies](#4-installing-dependencies)
5. [IBM Granite Setup (Local)](#5-ibm-granite-setup-local)
6. [Vision Model Setup](#6-vision-model-setup)
7. [Project Configuration](#7-project-configuration)
8. [Running the Application](#8-running-the-application)
9. [Verification & Testing](#9-verification--testing)
10. [Troubleshooting](#10-troubleshooting)
11. [Optional Enhancements](#11-optional-enhancements)

---

## 1. Prerequisites

### 1.1 Required Software

Before starting, ensure you have:

- **Windows 11** (or Windows 10)
- **PowerShell 5.1+** (comes with Windows)
- **NVIDIA GPU** with CUDA support (GTX 1060 or better)
- **Internet connection** (for initial setup)
- **Administrator access** (for some installations)

### 1.2 Hardware Checklist

| Component | Minimum | Recommended | Your System |
|-----------|---------|-------------|-------------|
| **CPU** | 4 cores | 8 cores | ☐ |
| **RAM** | 8GB | 16GB | ☐ |
| **GPU** | GTX 1060 (6GB) | RTX 3060 (12GB) | ☐ |
| **Storage** | 10GB free | 20GB free | ☐ |
| **CUDA** | 11.8+ | 12.0+ | ☐ |

### 1.3 Check Your GPU

Open PowerShell and run:

```powershell
nvidia-smi
```

**Expected Output:**
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.xx       Driver Version: 535.xx       CUDA Version: 12.x   |
|-------------------------------+----------------------+----------------------+
| GPU  Name            TCC/WDDM | Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  NVIDIA GeForce ... WDDM  | 00000000:01:00.0  On |                  N/A |
```

✅ If you see this, your GPU is ready!  
❌ If not, install NVIDIA drivers from: https://www.nvidia.com/Download/index.aspx

---

## 2. System Requirements Check

### 2.1 Check Python Installation

```powershell
python --version
```

**Expected:** `Python 3.8.x` or higher

If not installed:
1. Download from: https://www.python.org/downloads/
2. **Important:** Check "Add Python to PATH" during installation
3. Restart PowerShell after installation

### 2.2 Check CUDA Installation

```powershell
nvcc --version
```

**Expected:** `Cuda compilation tools, release 11.8` or higher

If not installed:
1. Download CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
2. Choose: Windows → x86_64 → 11 → exe (local)
3. Install with default settings
4. Restart computer

### 2.3 Check Git (Optional but Recommended)

```powershell
git --version
```

If not installed:
1. Download from: https://git-scm.com/download/win
2. Install with default settings

---

## 3. Python Environment Setup

### 3.1 Navigate to Project Directory

```powershell
cd c:\Projects\RecipeAI
```

If the directory doesn't exist:

```powershell
mkdir c:\Projects\RecipeAI
cd c:\Projects\RecipeAI
```

### 3.2 Create Virtual Environment

**Why?** Isolates project dependencies from system Python.

```powershell
python -m venv venv
```

This creates a `venv` folder in your project directory.

### 3.3 Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

**Expected:** Your prompt should now show `(venv)` at the beginning:
```
(venv) PS C:\Projects\RecipeAI>
```

**Troubleshooting:** If you get an execution policy error:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

### 3.4 Upgrade pip

```powershell
python -m pip install --upgrade pip
```

---

## 4. Installing Dependencies

### 4.1 Create requirements.txt

Create a file named `requirements.txt` in `c:\Projects\RecipeAI\` with:

```txt
torch>=2.0.0
torchvision>=0.15.0
transformers>=4.30.0
qwen-vl-utils>=0.1.0
ibm-watsonx-ai>=0.2.0
pillow>=9.0.0
numpy>=1.24.0
accelerate>=0.20.0
```

### 4.2 Install PyTorch with CUDA

**Important:** Install PyTorch first with CUDA support.

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**This will take 5-10 minutes** (downloading ~2GB).

### 4.3 Verify PyTorch CUDA

```powershell
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"
```

**Expected Output:**
```
CUDA available: True
CUDA version: 11.8
Device: NVIDIA GeForce RTX 3060
```

✅ If `CUDA available: True`, proceed!  
❌ If `False`, reinstall PyTorch with correct CUDA version.

### 4.4 Install Remaining Dependencies

```powershell
pip install transformers qwen-vl-utils ibm-watsonx-ai pillow numpy accelerate
```

**This will take 3-5 minutes.**

### 4.5 Verify Installation

```powershell
pip list
```

Check that these packages are installed:
- ✅ torch
- ✅ transformers
- ✅ qwen-vl-utils
- ✅ ibm-watsonx-ai
- ✅ pillow
- ✅ numpy

---

## 5. IBM Granite Setup (Local)

### 5.1 Option A: Using IBM Watsonx.ai API (Recommended for Students)

**Step 1:** Get IBM Cloud Account
1. Go to: https://cloud.ibm.com/registration
2. Sign up with your student email
3. Verify your email

**Step 2:** Create Watsonx.ai Project
1. Go to: https://dataplatform.cloud.ibm.com/
2. Click "Create a project" → "Create an empty project"
3. Name it "RecipeAI"
4. Note your **Project ID** (found in project settings)

**Step 3:** Get API Key
1. Go to: https://cloud.ibm.com/iam/apikeys
2. Click "Create an IBM Cloud API key"
3. Name it "RecipeAI-Key"
4. **Copy and save the API key** (you won't see it again!)

**Step 4:** Configure Environment Variables

Create a file named `.env` in `c:\Projects\RecipeAI\`:

```env
IBM_API_KEY=your_api_key_here
IBM_PROJECT_ID=your_project_id_here
IBM_URL=https://us-south.ml.cloud.ibm.com
```

Replace `your_api_key_here` and `your_project_id_here` with your actual values.

**Step 5:** Install python-dotenv

```powershell
pip install python-dotenv
```

**Step 6:** Update granite.py

Add at the top of `granite.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("IBM_API_KEY")
PROJECT_ID = os.getenv("IBM_PROJECT_ID")
```

### 5.2 Option B: Local Granite with Ollama (No API Required)

**For completely offline deployment:**

**Step 1:** Install Ollama
1. Download from: https://ollama.ai/download
2. Run installer
3. Restart PowerShell

**Step 2:** Download Granite Model

```powershell
ollama pull granite:8b
```

**This will download ~4.5GB** (takes 10-20 minutes).

**Step 3:** Test Ollama

```powershell
ollama run granite:8b "Hello, how are you?"
```

**Step 4:** Create granite_local.py

```python
from ollama import Client

client = Client(host='http://localhost:11434')

def get_recommendation(ingredients, recipes):
    prompt = f"""
You are a sustainable cooking assistant.
Available ingredients: {ingredients}
Recipe candidates: {recipes}

Choose the best recipe that reduces food waste.
Return:
Recipe Name: <name>
Reason: <explanation>
Missing Ingredients: <list or 'None'>
Waste Reduction Score: <1-10>
Cooking Instructions: <steps>
"""
    
    response = client.generate(
        model='granite:8b',
        prompt=prompt
    )
    return response['response']
```

---

## 6. Vision Model Setup

### 6.1 Download Qwen2.5-VL Model

The model will download automatically on first run, but you can pre-download:

```powershell
python -c "from transformers import AutoProcessor; AutoProcessor.from_pretrained('Qwen/Qwen2.5-VL-3B-Instruct')"
```

**This downloads ~6GB** (takes 15-30 minutes).

**Progress indicators:**
```
Downloading: 100%|████████████████████| 6.2G/6.2G [15:23<00:00, 6.7MB/s]
```

### 6.2 Verify Model Download

```powershell
python -c "from transformers import Qwen2_5_VLForConditionalGeneration; print('Model available!')"
```

**Expected:** `Model available!`

### 6.3 Model Storage Location

Models are stored in:
```
C:\Users\<YourUsername>\.cache\huggingface\hub\
```

**Size:** ~6GB for Qwen2.5-VL-3B

---

## 7. Project Configuration

### 7.1 Verify Project Files

Ensure these files exist in `c:\Projects\RecipeAI\`:

```
RecipeAI/
├── vision.py              ✅
├── granite.py             ✅
├── recipe_matcher.py      ✅
├── recipes.json           ✅
├── samples/
│   ├── fridge_1.jpeg     ✅
│   └── fridge_2.png      ✅
├── .env                   ✅ (if using API)
├── requirements.txt       ✅
└── venv/                  ✅
```

### 7.2 Create .gitignore

Create `.gitignore` file:

```gitignore
# Environment
venv/
.env
*.env

# Cache
ingredient_cache.json
__pycache__/
*.pyc
*.pyo

# Models (optional - if you want to exclude cached models)
.cache/

# IDE
.vscode/
.idea/
*.swp

# OS
Thumbs.db
.DS_Store
```

### 7.3 Initialize Git Repository (Optional)

```powershell
git init
git add .
git commit -m "Initial commit: RecipeAI setup"
```

---

## 8. Running the Application

### 8.1 First Run (Cache Miss)

```powershell
python vision.py
```

**Expected Output:**
```
1. Starting extraction process

⚠️ [CACHE MISS] Processing new image (abc123...)...

[Cache Miss] Loading Qwen Model into VRAM...
Model loaded successfully!
2. Messages created (0.0234s)
3. Chat template done (0.0156s)
4. Vision processing done (0.7823s)
5. Processor done (0.1234s)
6. Moved to GPU (0.0456s)
5.234 GB allocated
6.123 GB reserved
7. Starting generation
8. Generation finished (2.1234s)

RAW RESPONSE FROM QWEN:
tomato, onion, cucumber, carrot, milk, bread

💾 New entry saved to local cache.
9. Post-processing done (0.0123s)
--- Total pipeline extraction time: 7.4567s ---

Detected Ingredients:
['tomato', 'onion', 'cucumber', 'carrot', 'milk', 'bread']

Top Recipe Matches:
Masala Bread Upma | 66.67%
Spicy Roti Upma | 66.67%
Leftover Roti Frankie | 50.0%
...

Fetching final reasoning breakdown from IBM Granite...

Granite Recommendation:
Recipe Name: Masala Bread Upma
Reason: This recipe maximizes the use of available ingredients...
Missing Ingredients: None
Waste Reduction Score: 9/10 - Excellent use of stale bread...
Cooking Instructions:
1. Heat oil in a pan...
2. Add onions and tomatoes...
...
```

### 8.2 Second Run (Cache Hit)

```powershell
python vision.py
```

**Expected Output:**
```
1. Starting extraction process

🚀 [CACHE HIT] Found image match (abc123...)!
--- Total pipeline extraction time: 0.0234s ---

Detected Ingredients:
['tomato', 'onion', 'cucumber', 'carrot', 'milk', 'bread']
...
```

**Notice:** 375x faster! (7.5s → 0.02s)

### 8.3 Test with Different Images

```powershell
# Edit vision.py, change line 187:
# ingredients = extract_ingredients("samples/fridge_1.jpeg")

python vision.py
```

---

## 9. Verification & Testing

### 9.1 Quick Verification Script

Create `test_setup.py`:

```python
import torch
from transformers import AutoProcessor
import json
import os

print("=== RecipeAI Setup Verification ===\n")

# 1. Python version
import sys
print(f"✓ Python: {sys.version.split()[0]}")

# 2. PyTorch & CUDA
print(f"✓ PyTorch: {torch.__version__}")
print(f"✓ CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"✓ GPU: {torch.cuda.get_device_name(0)}")
    print(f"✓ CUDA Version: {torch.version.cuda}")

# 3. Transformers
import transformers
print(f"✓ Transformers: {transformers.__version__}")

# 4. Project files
files = ['vision.py', 'granite.py', 'recipe_matcher.py', 'recipes.json']
for f in files:
    if os.path.exists(f):
        print(f"✓ {f} exists")
    else:
        print(f"✗ {f} missing!")

# 5. Sample images
samples = ['samples/fridge_1.jpeg', 'samples/fridge_2.png']
for s in samples:
    if os.path.exists(s):
        print(f"✓ {s} exists")
    else:
        print(f"✗ {s} missing!")

# 6. Environment variables (if using API)
if os.path.exists('.env'):
    print("✓ .env file exists")
    from dotenv import load_dotenv
    load_dotenv()
    if os.getenv('IBM_API_KEY'):
        print("✓ IBM_API_KEY configured")
    if os.getenv('IBM_PROJECT_ID'):
        print("✓ IBM_PROJECT_ID configured")

print("\n=== Setup Complete! ===")
```

Run it:

```powershell
python test_setup.py
```

**Expected:** All items should show ✓

### 9.2 Test Individual Components

**Test Recipe Matcher:**

```powershell
python -c "from recipe_matcher import find_best_recipes; recipes = find_best_recipes(['rice', 'curd'], top_n=3); print(recipes[0])"
```

**Expected:**
```python
{'name': 'Curd Rice', 'score': 100.0, 'matched': ['rice', 'curd'], 'missing': [], 'target': 'leftover rice'}
```

**Test Vision (with cache):**

```powershell
python -c "from vision import extract_ingredients; print(extract_ingredients('samples/fridge_2.png'))"
```

### 9.3 Performance Benchmark

Create `benchmark.py`:

```python
import time
from vision import extract_ingredients

image_path = "samples/fridge_2.png"

# First run (cache miss)
print("First run (cache miss)...")
start = time.time()
ingredients1 = extract_ingredients(image_path)
time1 = time.time() - start
print(f"Time: {time1:.2f}s")
print(f"Ingredients: {ingredients1}\n")

# Second run (cache hit)
print("Second run (cache hit)...")
start = time.time()
ingredients2 = extract_ingredients(image_path)
time2 = time.time() - start
print(f"Time: {time2:.4f}s")
print(f"Ingredients: {ingredients2}\n")

# Calculate speedup
speedup = time1 / time2
print(f"Speedup: {speedup:.0f}x faster!")
```

Run:

```powershell
python benchmark.py
```

**Expected:**
```
First run (cache miss)...
Time: 7.45s
Ingredients: ['tomato', 'onion', ...]

Second run (cache hit)...
Time: 0.0234s
Ingredients: ['tomato', 'onion', ...]

Speedup: 318x faster!
```

---

## 10. Troubleshooting

### 10.1 Common Issues

#### Issue 1: "CUDA not available"

**Symptoms:**
```python
CUDA available: False
```

**Solutions:**
1. Check GPU driver:
   ```powershell
   nvidia-smi
   ```
2. Reinstall PyTorch with CUDA:
   ```powershell
   pip uninstall torch torchvision
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```
3. Verify CUDA installation:
   ```powershell
   nvcc --version
   ```

#### Issue 2: "Out of Memory" Error

**Symptoms:**
```
RuntimeError: CUDA out of memory
```

**Solutions:**
1. Close other GPU applications
2. Reduce batch size (already 1 in our code)
3. Use half precision (already using `torch.float16`)
4. Clear cache:
   ```python
   import torch
   torch.cuda.empty_cache()
   ```

#### Issue 3: "Module not found"

**Symptoms:**
```
ModuleNotFoundError: No module named 'transformers'
```

**Solutions:**
1. Ensure virtual environment is activated:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
2. Reinstall dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

#### Issue 4: "API Key Error"

**Symptoms:**
```
GraniteAPIException: Invalid API key
```

**Solutions:**
1. Check `.env` file exists
2. Verify API key is correct (no extra spaces)
3. Test API key:
   ```powershell
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('IBM_API_KEY'))"
   ```

#### Issue 5: Slow First Run

**Symptoms:**
First run takes 10+ seconds

**This is normal!** The model needs to:
1. Load into VRAM (~4.5s)
2. Process image (~2.2s)
3. Generate output (~1.5s)

**Solutions:**
- Use caching (automatic)
- Pre-load model at startup
- Use smaller model (trade-off: accuracy)

### 10.2 Debug Mode

Add to `vision.py` for detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 10.3 Clear Cache

If you need to reset:

```powershell
Remove-Item ingredient_cache.json
```

### 10.4 Check GPU Memory

```powershell
python -c "import torch; print(f'Allocated: {torch.cuda.memory_allocated()/1024**3:.2f}GB'); print(f'Reserved: {torch.cuda.memory_reserved()/1024**3:.2f}GB')"
```

### 10.5 Getting Help

If issues persist:

1. **Check logs:** Look at error messages carefully
2. **Search GitHub Issues:** https://github.com/QwenLM/Qwen-VL/issues
3. **IBM Watsonx Docs:** https://www.ibm.com/docs/en/watsonx-as-a-service
4. **Stack Overflow:** Tag with `pytorch`, `transformers`, `cuda`

---

## 11. Optional Enhancements

### 11.1 Install Jupyter Notebook

For interactive development:

```powershell
pip install jupyter notebook
jupyter notebook
```

### 11.2 Install Testing Framework

```powershell
pip install pytest pytest-cov
```

Create `tests/test_basic.py`:

```python
def test_recipe_matcher():
    from recipe_matcher import find_best_recipes
    recipes = find_best_recipes(['rice', 'curd'], top_n=1)
    assert recipes[0]['name'] == 'Curd Rice'
    assert recipes[0]['score'] == 100.0
```

Run tests:

```powershell
pytest tests/ -v
```

### 11.3 Install Code Formatter

```powershell
pip install black
black *.py
```

### 11.4 Install Linter

```powershell
pip install pylint
pylint vision.py
```

### 11.5 Create Batch Script

Create `run.bat`:

```batch
@echo off
call venv\Scripts\activate.bat
python vision.py
pause
```

Double-click to run!

### 11.6 Add More Sample Images

Place your own fridge images in `samples/` directory:

```
samples/
├── fridge_1.jpeg
├── fridge_2.png
├── my_fridge.jpg      ← Add yours!
└── pantry.png         ← Add yours!
```

Update `vision.py` line 187 to test:

```python
ingredients = extract_ingredients("samples/my_fridge.jpg")
```

---

## Quick Start Summary

**For the impatient developer:**

```powershell
# 1. Setup
cd c:\Projects\RecipeAI
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install transformers qwen-vl-utils ibm-watsonx-ai pillow numpy accelerate python-dotenv

# 3. Configure
# Create .env with your IBM credentials

# 4. Run
python vision.py

# 5. Enjoy! 🎉
```

---

## Next Steps

After successful setup:

1. ✅ Read [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md) for implementation details
2. ✅ Read [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md) for system architecture
3. ✅ Read [SUSTAINABILITY_METRICS.md](SUSTAINABILITY_METRICS.md) for impact tracking
4. ✅ Experiment with different images
5. ✅ Add more recipes to `recipes.json`
6. ✅ Customize prompts for better results
7. ✅ Build a web interface (Flask/FastAPI)
8. ✅ Deploy to cloud (AWS/Azure/GCP)

---

## Support & Resources

**Documentation:**
- Project Concept: [PROJECT_CONCEPT.md](PROJECT_CONCEPT.md)
- Technical Guide: [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md)
- Architecture: [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)
- Metrics: [SUSTAINABILITY_METRICS.md](SUSTAINABILITY_METRICS.md)

**External Resources:**
- PyTorch: https://pytorch.org/docs/
- Transformers: https://huggingface.co/docs/transformers/
- Qwen-VL: https://github.com/QwenLM/Qwen-VL
- IBM Watsonx: https://www.ibm.com/watsonx
- CUDA: https://developer.nvidia.com/cuda-toolkit

**Community:**
- Hugging Face Forums: https://discuss.huggingface.co/
- PyTorch Forums: https://discuss.pytorch.org/
- IBM Community: https://community.ibm.com/

---

**Document Version:** 1.0  
**Last Updated:** June 19, 2026  
**Maintained By:** RecipeAI Team

🎉 **Congratulations! Your RecipeAI system is ready to reduce food waste!** 🎉