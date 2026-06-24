/**
 * API utility functions for RecipeAI frontend
 * Handles all communication with the FastAPI backend
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for AI processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    if (error.response) {
      // Server responded with error status
      throw new Error(error.response.data.detail || 'Server error occurred');
    } else if (error.request) {
      // Request made but no response
      throw new Error('No response from server. Please check if the backend is running.');
    } else {
      // Error in request setup
      throw new Error(error.message || 'Request failed');
    }
  }
);

/**
 * Upload an image file
 * @param {File} file - Image file to upload
 * @returns {Promise<Object>} Upload response with file path
 */
export const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/upload-image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Detect ingredients from uploaded image
 * @param {string} filePath - Path to uploaded image
 * @returns {Promise<Object>} Detected ingredients and metadata
 */
export const detectIngredients = async (filePath) => {
  const response = await api.post('/api/detect-ingredients', null, {
    params: { file_path: filePath },
  });

  return response.data;
};

/**
 * Match recipes based on ingredients
 * @param {string[]} ingredients - List of ingredients
 * @param {number} topN - Number of top recipes to return
 * @param {string} dietaryPreference - Dietary preference filter ('all', 'vegetarian', 'non-vegetarian')
 * @param {string} sortBy - Sorting strategy ('match_percentage' or 'ingredients_used')
 * @returns {Promise<Object>} Matched recipes
 */
export const matchRecipes = async (ingredients, topN = 5, dietaryPreference = null, sortBy = 'match_percentage') => {
  const params = { top_n: topN };
  if (dietaryPreference && dietaryPreference !== 'all') {
    params.dietary_preference = dietaryPreference;
  }
  if (sortBy && sortBy !== 'match_percentage') {
    params.sort_by = sortBy;
  }

  const response = await api.post('/api/match-recipes', ingredients, {
    params,
  });

  return response.data;
};

/**
 * Get sustainability analysis for a recipe
 * @param {string[]} userIngredients - User's available ingredients
 * @param {Object} recipeData - Recipe data object
 * @returns {Promise<Object>} Sustainability report
 */
export const getSustainabilityAnalysis = async (userIngredients, recipeData) => {
  const response = await api.post('/api/sustainability-analysis', {
    user_ingredients: userIngredients,
    recipe_data: recipeData,
  });

  return response.data;
};

/**
 * Get AI recommendation from Granite
 * @param {string[]} ingredients - Available ingredients
 * @param {string[]} recipes - Recipe names
 * @param {Object} topRecipe - Top recipe details (optional)
 * @returns {Promise<Object>} AI recommendation
 */
export const getAIRecommendation = async (ingredients, recipes, topRecipe = null) => {
  const response = await api.post('/api/ai-recommendation', {
    ingredients,
    recipes,
    top_recipe: topRecipe,
  });

  return response.data;
};

/**
 * Run complete analysis pipeline
 * @param {string} filePath - Path to uploaded image
 * @param {string} dietaryPreference - Dietary preference filter ('all', 'vegetarian', 'non-vegetarian')
 * @returns {Promise<Object>} Complete analysis results
 */
export const runFullAnalysis = async (filePath, dietaryPreference = null) => {
  const params = { file_path: filePath };
  if (dietaryPreference && dietaryPreference !== 'all') {
    params.dietary_preference = dietaryPreference;
  }

  const response = await api.post('/api/full-analysis', null, {
    params,
  });

  return response.data;
};

/**
 * Get list of sample images
 * @returns {Promise<Object>} List of sample images
 */
export const getSampleImages = async () => {
  const response = await api.get('/api/sample-images');
  return response.data;
};

/**
 * Health check
 * @returns {Promise<Object>} Health status
 */
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

/**
 * Process image with progress tracking using Server-Sent Events (SSE)
 * @param {File} file - Image file
 * @param {Function} onProgress - Progress callback
 * @param {string} dietaryPreference - Dietary preference filter ('all', 'vegetarian', 'non-vegetarian')
 * @param {string} sortBy - Sorting strategy ('match_percentage' or 'ingredients_used')
 * @returns {Promise<Object>} Analysis results
 */
export const processImageWithProgress = async (file, onProgress, dietaryPreference = null, sortBy = 'match_percentage') => {
  try {
    // Stage 1: Upload image
    onProgress({ stage: 'upload', message: 'Uploading image...', progress: 10 });
    const uploadResult = await uploadImage(file);
    const filePath = uploadResult.file_path;

    // Stage 2-5: SSE streaming request
    const url = `${API_BASE_URL}/api/analysis-stream?file_path=${encodeURIComponent(filePath)}` + 
                (dietaryPreference && dietaryPreference !== 'all' ? `&dietary_preference=${dietaryPreference}` : '') +
                `&sort_by=${sortBy}`;
                
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Accept': 'text/event-stream'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Failed to initialize stream: ${response.statusText}`);
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    
    let finalResult = null;
    let currentData = {
      ingredients: [],
      labeledImageUrl: null,
      recipes: [],
      sustainability: null,
      aiRecommendation: null,
      sustainabilityTips: null
    };
    
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      
      const lines = buffer.split('\n');
      buffer = lines.pop(); // Keep partial line in buffer
      
      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('data: ')) {
          const dataStr = trimmed.slice(6);
          try {
            const eventData = JSON.parse(dataStr);
            
            if (eventData.stage === 'error') {
              throw new Error(eventData.message);
            }
            
            // Accumulate partial data as it streams in to update UI incrementally
            if (eventData.data) {
              if (eventData.stage === 'detection') {
                currentData.ingredients = eventData.data.ingredients;
                currentData.labeledImageUrl = eventData.data.labeled_image_url;
              } else if (eventData.stage === 'matching') {
                currentData.recipes = eventData.data.recipes;
              } else if (eventData.stage === 'sustainability') {
                currentData.sustainability = eventData.data.sustainability;
              } else if (eventData.stage === 'ai') {
                currentData.aiRecommendation = eventData.data.ai_recommendation;
                currentData.sustainabilityTips = eventData.data.sustainability_tips;
              }
            }
            
            // Trigger progress callback with current accumulated data
            onProgress({
              stage: eventData.stage,
              message: eventData.message,
              progress: eventData.progress,
              data: currentData
            });
            
            if (eventData.stage === 'complete' && eventData.data) {
              finalResult = {
                ingredients: eventData.data.ingredients,
                labeledImageUrl: eventData.data.labeled_image_url,
                recipes: eventData.data.recipes,
                topRecipe: eventData.data.top_recipe,
                sustainability: eventData.data.sustainability,
                aiRecommendation: eventData.data.ai_recommendation,
                sustainabilityTips: eventData.data.sustainability_tips,
                processingTimes: {
                  total: 0 // placeholder
                }
              };
            }
          } catch (err) {
            console.error('Failed to parse SSE line:', line, err);
            if (err.message && err.message.includes('Analysis failed')) {
              throw err;
            }
          }
        }
      }
    }
    
    if (!finalResult) {
      throw new Error('Analysis completed but returned no results');
    }
    
    return finalResult;
  } catch (error) {
    onProgress({ stage: 'error', message: error.message, progress: 0 });
    throw error;
  }
};

/**
 * Send a chat message to the AI Chef chatbot (Granite)
 * @param {string} message - User message
 * @param {Array} history - Message history [{"role": "user", "content": "..."}, ...]
 * @param {string[]} ingredients - List of ingredients
 * @param {string} currentRecipe - Current recipe name (optional)
 * @returns {Promise<Object>} Response from Chef
 */
export const chatWithChef = async (message, history = [], ingredients = [], currentRecipe = null) => {
  const response = await api.post('/api/chat', {
    message,
    history,
    ingredients,
    current_recipe: currentRecipe,
  });
  return response.data;
};

export default api;

// Made with Bob
