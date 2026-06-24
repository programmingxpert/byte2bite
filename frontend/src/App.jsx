import React, { useState, useEffect } from 'react';
import { Sparkles, RefreshCw, Moon, Sun, ShoppingBag } from 'lucide-react';
import ImageUpload from './components/ImageUpload';
import LoadingStages from './components/LoadingStage';
import IngredientsList from './components/IngredientsList';
import RecipesList from './components/RecipeCard';
import SustainabilityMetrics from './components/SustainabilityMetrics';
import AIRecommendations from './components/AIRecommendations';
import ShoppingList from './components/ShoppingList';
import { processImageWithProgress, matchRecipes, getSustainabilityAnalysis, getAIRecommendation } from './utils/api';


function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStage, setCurrentStage] = useState('');
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [dietaryPreference, setDietaryPreference] = useState('all');
  const [sortBy, setSortBy] = useState('match_percentage');
  
  // Dark mode state with localStorage persistence
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });

  // Apply dark mode to document root
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  const [isRecalculating, setIsRecalculating] = useState(false);
  const [shoppingList, setShoppingList] = useState(() => {
    const saved = localStorage.getItem('shoppingList');
    return saved ? JSON.parse(saved) : [];
  });
  const [isShoppingOpen, setIsShoppingOpen] = useState(false);

  useEffect(() => {
    localStorage.setItem('shoppingList', JSON.stringify(shoppingList));
  }, [shoppingList]);

  const handleIngredientsChange = (newIngredients) => {
    setResults(prev => ({
      ...prev,
      ingredients: newIngredients
    }));
  };

  const handleRecalculate = async () => {
    if (!results || !results.ingredients || results.ingredients.length === 0) return;
    
    setIsRecalculating(true);
    setError(null);
    
    try {
      // 1. Match recipes
      const recipesResult = await matchRecipes(results.ingredients, 20, dietaryPreference, sortBy);
      const newRecipes = recipesResult.recipes;
      
      if (!newRecipes || newRecipes.length === 0) {
        throw new Error('No matching recipes found for updated ingredients');
      }
      
      const topRecipe = newRecipes[0];
      
      // 2. Get sustainability report for top recipe
      const sustainabilityResult = await getSustainabilityAnalysis(
        results.ingredients.map(i => typeof i === 'string' ? i : i.name),
        topRecipe
      );
      
      // 3. Get AI recommendation
      const recipeNames = newRecipes.map(r => r.name);
      const aiResult = await getAIRecommendation(
        results.ingredients.map(i => typeof i === 'string' ? i : i.name),
        recipeNames,
        topRecipe
      );
      
      setResults(prev => ({
        ...prev,
        recipes: newRecipes,
        topRecipe: topRecipe,
        sustainability: sustainabilityResult.report,
        aiRecommendation: aiResult.recommendation,
        sustainabilityTips: aiResult.sustainabilityTips || prev.sustainabilityTips
      }));
    } catch (err) {
      setError(err.message || 'Failed to recalculate recipes');
    } finally {
      setIsRecalculating(false);
    }
  };

  const handleAddToShoppingList = (missingIngredients) => {
    if (!missingIngredients) return;
    
    setShoppingList(prev => {
      let updated = [...prev];
      missingIngredients.forEach(item => {
        const name = typeof item === 'string' ? item : item.name;
        const exists = updated.find(i => i.name.toLowerCase() === name.toLowerCase());
        if (!exists) {
          updated.push({ name, checked: false, note: 'Needed for recipe' });
        }
      });
      return updated;
    });
    setIsShoppingOpen(true);
  };

  const handleAddShoppingItem = (name) => {
    setShoppingList(prev => {
      const exists = prev.find(i => i.name.toLowerCase() === name.toLowerCase());
      if (exists) return prev;
      return [...prev, { name, checked: false, note: 'Custom item' }];
    });
  };

  const handleRemoveShoppingItem = (index) => {
    setShoppingList(prev => prev.filter((_, idx) => idx !== index));
  };

  const handleToggleShoppingItem = (index) => {
    setShoppingList(prev => prev.map((item, idx) => {
      if (idx === index) {
        return { ...item, checked: !item.checked };
      }
      return item;
    }));
  };

  const handleClearCheckedShoppingItems = () => {
    setShoppingList(prev => prev.filter(item => !item.checked));
  };

  const handleImageSelect = (file) => {
    setSelectedFile(file);
    setResults(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('Please select an image first');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResults(null);
    setProgress(0);

    try {
      const result = await processImageWithProgress(
        selectedFile,
        (status) => {
          setCurrentStage(status.stage);
          setProgress(status.progress);
        },
        dietaryPreference,
        sortBy
      );

      setResults(result);
      setCurrentStage('complete');
    } catch (err) {
      setError(err.message || 'An error occurred during analysis');
      setCurrentStage('error');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setResults(null);
    setError(null);
    setCurrentStage('');
    setProgress(0);
    setDietaryPreference('all');
    setSortBy('match_percentage');
  };

  const handleDietaryChange = (preference) => {
    setDietaryPreference(preference);
    // Clear results when dietary preference changes
    if (results) {
      setResults(null);
    }
  };

  const handleSortChange = async (newSortBy) => {
    if (newSortBy === sortBy || !results || !results.ingredients) {
      return;
    }

    setSortBy(newSortBy);
    setIsProcessing(true);
    setError(null);

    try {
      // Re-fetch recipes with new sorting using the statically imported function
      const recipesResult = await matchRecipes(results.ingredients, 5, dietaryPreference, newSortBy);
      
      // Update results with new recipe order
      setResults({
        ...results,
        recipes: recipesResult.recipes,
        topRecipe: recipesResult.recipes[0],
      });
    } catch (err) {
      setError(err.message || 'Failed to re-sort recipes');
    } finally {
      setIsProcessing(false);
    }
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 transition-colors duration-200">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50 transition-colors duration-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-br from-primary-500 to-green-500 rounded-xl">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-green-600 bg-clip-text text-transparent">
                  Byte2Bite
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Smart Recipe Recommendations with Sustainability Analysis
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={() => setIsShoppingOpen(true)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors relative"
                title="Open Shopping List"
              >
                <ShoppingBag className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                {shoppingList.length > 0 && (
                  <span className="absolute -top-1 -right-1 bg-blue-500 text-white rounded-full text-xs w-4 h-4 flex items-center justify-center font-bold">
                    {shoppingList.filter(item => !item.checked).length}
                  </span>
                )}
              </button>

              <button
                onClick={toggleDarkMode}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {darkMode ? (
                  <Sun className="w-5 h-5 text-yellow-500" />
                ) : (
                  <Moon className="w-5 h-5 text-gray-600" />
                )}
              </button>

              {results && (
                <button
                  onClick={handleReset}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>New Analysis</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Upload Section */}
          {!results && (
            <div className="max-w-2xl mx-auto">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                  Upload Your Fridge Photo
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Let AI detect ingredients and recommend sustainable recipes
                </p>
              </div>

              <ImageUpload
                onImageSelect={handleImageSelect}
                disabled={isProcessing}
                dietaryPreference={dietaryPreference}
                onDietaryChange={handleDietaryChange}
                darkMode={darkMode}
              />

              {selectedFile && !isProcessing && (
                <div className="mt-6 text-center">
                  <button
                    onClick={handleAnalyze}
                    className="btn-primary text-lg px-8 py-4 flex items-center space-x-2 mx-auto"
                  >
                    <Sparkles className="w-5 h-5" />
                    <span>Analyze with AI</span>
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="max-w-2xl mx-auto card bg-red-50 dark:bg-red-900 border-2 border-red-200 dark:border-red-700 animate-shake">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <svg className="w-6 h-6 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-red-800 dark:text-red-200 mb-1">
                    Analysis Failed
                  </h3>
                  <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Loading Stages */}
          {isProcessing && (
            <div className="max-w-2xl mx-auto">
              <div className="card">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                  Processing Your Image...
                </h3>
                <LoadingStages currentStage={currentStage} progress={progress} darkMode={darkMode} />
              </div>
            </div>
          )}

          {/* Results Display */}
          {results && (
            <div className="space-y-8">
              {/* Ingredients */}
              <IngredientsList
                ingredients={results.ingredients}
                labeledImageUrl={results.labeledImageUrl}
                cacheHit={results.processingTimes?.ingredients < 1}
                darkMode={darkMode}
                onIngredientsChange={handleIngredientsChange}
                onRecalculate={handleRecalculate}
                isRecalculating={isRecalculating}
              />

              {/* Recipes */}
              <RecipesList
                recipes={results.recipes}
                darkMode={darkMode}
                sortBy={sortBy}
                onSortChange={handleSortChange}
                onAddToShoppingList={handleAddToShoppingList}
              />

              {/* Sustainability Metrics */}
              <SustainabilityMetrics sustainability={results.sustainability} darkMode={darkMode} />

              {/* AI Recommendations */}
              <AIRecommendations
                recommendation={results.aiRecommendation}
                tips={results.sustainabilityTips}
                ingredients={results.ingredients}
                recipeName={results.topRecipe?.name}
                darkMode={darkMode}
              />

              {/* Processing Times */}
              {results.processingTimes && (
                <div className="card bg-gray-50 dark:bg-gray-800">
                  <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                    Processing Performance
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(results.processingTimes).map(([key, time]) => (
                      <div key={key} className="text-center">
                        <p className="text-xs text-gray-600 dark:text-gray-400 capitalize mb-1">
                          {key.replace('_', ' ')}
                        </p>
                        <p className="text-lg font-bold text-primary-600 dark:text-primary-400">
                          {time.toFixed(2)}s
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Shopping List Drawer */}
      <ShoppingList
        items={shoppingList}
        isOpen={isShoppingOpen}
        onClose={() => setIsShoppingOpen(false)}
        onClear={handleClearCheckedShoppingItems}
        onRemoveItem={handleRemoveShoppingItem}
        onAddItem={handleAddShoppingItem}
        onToggleChecked={handleToggleShoppingItem}
      />

      {/* Footer */}
      <footer className="mt-16 py-8 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 transition-colors duration-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center text-sm text-gray-600 dark:text-gray-400">
            <p className="mb-2">
              <span className="font-semibold">Byte2Bite</span> - Powered by Qwen Vision AI & IBM Granite
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-500">
              Promoting UN SDG 12: Responsible Consumption and Production
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;

// Made with Bob
