# RecipeAI - Smart Recipe Recommendations with Sustainability Analysis

A modern web application that uses AI to detect ingredients from fridge photos and recommend sustainable recipes with comprehensive environmental impact analysis.

## 🌟 Features

- **AI-Powered Ingredient Detection**: Uses Qwen Vision AI to identify ingredients from images
- **Smart Recipe Matching**: Finds best recipe matches based on available ingredients
- **Sustainability Analysis**: Comprehensive environmental impact metrics including CO₂ savings
- **IBM Granite AI Recommendations**: Advanced AI-powered cooking suggestions
- **Real-time Progress Tracking**: Beautiful loading states showing each processing stage
- **Modern React UI**: Built with React 18, Vite, and TailwindCSS
- **RESTful API**: FastAPI backend with full documentation

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with Uvicorn
- **AI Models**: 
  - Qwen2.5-VL-3B-Instruct for vision
  - IBM Granite (via Ollama) for recommendations
- **Features**: CORS support, file uploads, caching, error handling

### Frontend (React + Vite)
- **Framework**: React 18 with Vite
- **Styling**: TailwindCSS with custom components
- **State Management**: React Hooks
- **API Client**: Axios with interceptors
- **Icons**: Lucide React

## 📋 Prerequisites

### Backend Requirements
- Python 3.11 or higher
- CUDA-capable GPU (for Qwen model)
- 8GB+ VRAM recommended
- Ollama installed (for Granite AI)

### Frontend Requirements
- Node.js 18+ and npm

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
cd c:/Projects/RecipeAI
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
# Install backend dependencies
pip install -r backend/requirements.txt

# Also install main project dependencies
pip install -r requirements.txt
```

#### Setup Ollama and Granite Model
```bash
# Install Ollama from https://ollama.ai
# Then pull the Granite model
ollama pull granite4:latest
```

#### Verify Backend Setup
```bash
# Test the backend
cd backend
python main.py
```

The backend will start on `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 3. Frontend Setup

#### Install Node Dependencies
```bash
cd frontend
npm install
```

#### Start Development Server
```bash
npm run dev
```

The frontend will start on `http://localhost:5173`

## 🎯 Running the Application

### Option 1: Run Both Servers Separately

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Option 2: Production Build

**Build Frontend:**
```bash
cd frontend
npm run build
```

**Serve with Backend:**
The built files will be in `frontend/dist/` and can be served by any static file server.

## 📁 Project Structure

```
RecipeAI/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Backend dependencies
│   └── __init__.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ImageUpload.jsx
│   │   │   ├── LoadingStage.jsx
│   │   │   ├── IngredientsList.jsx
│   │   │   ├── RecipeCard.jsx
│   │   │   ├── SustainabilityMetrics.jsx
│   │   │   └── AIRecommendations.jsx
│   │   ├── utils/
│   │   │   └── api.js          # API client
│   │   ├── styles/
│   │   │   └── App.css         # TailwindCSS styles
│   │   ├── App.jsx             # Main application
│   │   └── main.jsx            # Entry point
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
├── vision.py                   # Qwen vision model
├── recipe_matcher.py           # Recipe matching logic
├── granite.py                  # IBM Granite integration
├── sustainability_engine.py    # Sustainability calculations
├── recommendation_engine.py    # Recommendation logic
├── recipes.json                # Recipe database
├── samples/                    # Sample images
└── README.md
```

## 🔌 API Endpoints

### Core Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /api/upload-image` - Upload image file
- `POST /api/detect-ingredients` - Detect ingredients from image
- `POST /api/match-recipes` - Find matching recipes
- `POST /api/sustainability-analysis` - Get sustainability metrics
- `POST /api/ai-recommendation` - Get AI recommendations
- `POST /api/full-analysis` - Complete end-to-end analysis
- `GET /api/sample-images` - List available sample images

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

## 🎨 Frontend Features

### Components

1. **ImageUpload**: Drag-and-drop image upload with preview
2. **LoadingStages**: Real-time progress indicators for each processing stage
3. **IngredientsList**: Beautiful grid display of detected ingredients
4. **RecipeCard**: Detailed recipe cards with match percentages
5. **SustainabilityMetrics**: Comprehensive environmental impact visualization
6. **AIRecommendations**: IBM Granite AI-powered cooking suggestions

### Loading States

The application shows accurate loading states for:
- ✅ Uploading image (10%)
- ✅ Detecting ingredients with AI (30%)
- ✅ Matching recipes (50%)
- ✅ Calculating sustainability metrics (70%)
- ✅ Generating AI recommendations (90%)
- ✅ Complete (100%)

## 🌱 Sustainability Metrics

The application calculates and displays:

- **Ingredient Utilization**: Percentage of available ingredients used
- **Waste Reduction Score**: 0-10 rating based on ingredient usage
- **CO₂ Impact**: Carbon footprint savings from reducing food waste
- **SDG 12 Alignment**: UN Sustainable Development Goal alignment score
- **Environmental Equivalents**: CO₂ savings converted to km driven

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest
```

### Frontend Testing
```bash
cd frontend
npm run test
```

### Manual Testing
1. Start both servers
2. Open `http://localhost:5173`
3. Upload a fridge image (or use samples)
4. Click "Analyze with AI"
5. Watch the loading stages progress
6. Review results in organized sections

## 🐛 Troubleshooting

### Backend Issues

**CUDA Out of Memory:**
- Reduce batch size in vision.py
- Use smaller model variant
- Close other GPU applications

**Ollama Connection Failed:**
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve
```

**Module Import Errors:**
```bash
# Ensure you're in the correct directory
cd backend
python main.py
```

### Frontend Issues

**Port Already in Use:**
```bash
# Change port in vite.config.js or kill process
npx kill-port 5173
```

**API Connection Failed:**
- Verify backend is running on port 8000
- Check CORS settings in backend/main.py
- Ensure API_BASE_URL in frontend/src/utils/api.js is correct

**Build Errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 🔧 Configuration

### Backend Configuration
Edit `backend/main.py`:
```python
# Change port
uvicorn.run("main:app", host="0.0.0.0", port=8000)

# Update CORS origins
allow_origins=["http://localhost:5173", "http://localhost:3000"]
```

### Frontend Configuration
Edit `frontend/src/utils/api.js`:
```javascript
// Change API base URL
const API_BASE_URL = 'http://localhost:8000';
```

## 📊 Performance

- **Ingredient Detection**: 2-5 seconds (cached: <0.1s)
- **Recipe Matching**: <0.5 seconds
- **Sustainability Analysis**: <0.5 seconds
- **AI Recommendations**: 3-10 seconds (depends on Granite model)
- **Total Pipeline**: 5-15 seconds

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is part of a sustainability initiative promoting UN SDG 12.

## 🙏 Acknowledgments

- **Qwen Team**: For the excellent vision model
- **IBM**: For Granite AI model
- **Ollama**: For local AI model serving
- **FastAPI**: For the amazing web framework
- **React Team**: For the UI library
- **Vite**: For the blazing fast build tool

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check console logs for errors
4. Verify all dependencies are installed

## 🎯 Future Enhancements

- [ ] User authentication and saved recipes
- [ ] Recipe rating and feedback system
- [ ] Shopping list generation
- [ ] Meal planning calendar
- [ ] Mobile app version
- [ ] Multi-language support
- [ ] Voice input for ingredients
- [ ] Nutritional information
- [ ] Dietary restriction filters
- [ ] Social sharing features

---

**Made with ❤️ for a sustainable future**

Promoting UN SDG 12: Responsible Consumption and Production