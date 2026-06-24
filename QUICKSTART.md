# RecipeAI - Quick Start Guide

Get up and running with RecipeAI in 5 minutes!

## 🚀 Quick Setup

### Step 1: Install Backend Dependencies
```bash
pip install -r backend/requirements.txt
pip install -r requirements.txt
```

### Step 2: Install Ollama & Granite
```bash
# Download Ollama from https://ollama.ai
# Then run:
ollama pull granite4:latest
```

### Step 3: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

## ▶️ Running the Application

### Terminal 1 - Start Backend
```bash
cd backend
python main.py
```
✅ Backend running at: http://localhost:8000

### Terminal 2 - Start Frontend
```bash
cd frontend
npm run dev
```
✅ Frontend running at: http://localhost:5173

## 🎯 Using the Application

1. Open http://localhost:5173 in your browser
2. Upload a fridge photo (or use sample images)
3. Click "Analyze with AI"
4. Watch the magic happen! ✨

## 📊 What You'll See

### Loading Stages (with accurate progress):
- 🔄 Uploading image... (10%)
- 🤖 Detecting ingredients with AI... (30%)
- 🍳 Matching recipes... (50%)
- 🌱 Calculating sustainability metrics... (70%)
- 💡 Generating AI recommendations... (90%)
- ✅ Complete! (100%)

### Results Display:
1. **Detected Ingredients** - Grid of identified items
2. **Recipe Matches** - Top 5 recipes with match percentages
3. **Sustainability Metrics** - CO₂ savings, waste reduction scores
4. **AI Recommendations** - IBM Granite's cooking suggestions
5. **SDG 12 Alignment** - UN sustainability goal impact

## 🔧 Troubleshooting

### Backend won't start?
```bash
# Check Python version (need 3.11+)
python --version

# Verify CUDA is available
python -c "import torch; print(torch.cuda.is_available())"
```

### Frontend won't start?
```bash
# Check Node version (need 18+)
node --version

# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Ollama not working?
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve

# Verify Granite model
ollama run granite4:latest "Hello"
```

## 📝 API Documentation

Once backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎨 Key Features

✅ **Drag & Drop Upload** - Easy image upload interface  
✅ **Real-time Progress** - See exactly what's happening  
✅ **Beautiful UI** - Modern, responsive design  
✅ **Sustainability Focus** - Environmental impact metrics  
✅ **AI-Powered** - Qwen Vision + IBM Granite  
✅ **Fast Caching** - Instant results for repeated images  

## 💡 Pro Tips

1. **Use Good Photos**: Clear, well-lit images work best
2. **Check Cache**: Repeated images load instantly
3. **Sample Images**: Use provided samples in `/samples` folder
4. **API First**: Test endpoints at `/docs` before using UI
5. **Monitor Performance**: Check processing times in results

## 🆘 Need Help?

1. Check the main [README.md](README.md) for detailed docs
2. Review API docs at http://localhost:8000/docs
3. Check browser console for frontend errors
4. Check terminal for backend errors

## 🎯 Next Steps

- Try different fridge photos
- Explore the API documentation
- Check sustainability metrics
- Read AI recommendations
- Experiment with sample images

---

**Happy Cooking! 🍳🌱**

Made with ❤️ for sustainable living