import React, { useState } from 'react';
import { Apple, CheckCircle, Eye, EyeOff, Image as ImageIcon, Plus, Trash2, RotateCw, AlertTriangle } from 'lucide-react';

/**
 * IngredientsList Component
 * Displays detected ingredients in an interactive editor grid.
 * Allows adding, deleting, adjusting counts, and triggering recipe recalculation.
 */
const IngredientsList = ({ 
  ingredients, 
  onIngredientsChange, 
  onRecalculate, 
  isRecalculating, 
  labeledImageUrl, 
  cacheHit, 
  darkMode 
}) => {
  const [showLabeledImage, setShowLabeledImage] = useState(false);
  const [newIngredient, setNewIngredient] = useState('');
  const [newCount, setNewCount] = useState(1);

  if (!ingredients) {
    return null;
  }

  const commonIngredients = [
    "onion", "tomato", "potato", "lemon", "carrot", "capsicum", 
    "cucumber", "bread", "rice", "roti", "curd", "milk", "paneer", 
    "banana", "apple", "cheese", "butter", "garlic", "ginger", 
    "coriander", "salt", "oil", "sugar", "pepper", "chicken", "egg"
  ];

  // Ensure ingredients are normalized as objects { name, count }
  const normalizedIngredients = ingredients.map(item => {
    if (typeof item === 'string') {
      return { name: item, count: 1 };
    }
    return item;
  });

  const HIGH_RISK_PERISHABLES = ['milk', 'curd', 'paneer', 'banana', 'apple', 'tomato', 'cucumber', 'bread', 'roti'];

  const getSpoilageRisk = (name) => {
    const clean = name.toLowerCase().trim();
    if (HIGH_RISK_PERISHABLES.some(item => clean.includes(item))) {
      return 'high';
    }
    return 'low';
  };

  const handleCountChange = (name, delta) => {
    const updated = normalizedIngredients.map(item => {
      if (item.name === name) {
        const nextCount = Math.max(1, item.count + delta);
        return { ...item, count: nextCount };
      }
      return item;
    });
    onIngredientsChange(updated);
  };

  const handleDelete = (name) => {
    const updated = normalizedIngredients.filter(item => item.name !== name);
    onIngredientsChange(updated);
  };

  const handleAddIngredient = (e) => {
    e.preventDefault();
    const cleanName = newIngredient.trim().toLowerCase();
    if (!cleanName) return;

    // Check if it already exists
    const exists = normalizedIngredients.find(item => item.name === cleanName);
    let updated;
    if (exists) {
      updated = normalizedIngredients.map(item => {
        if (item.name === cleanName) {
          return { ...item, count: item.count + newCount };
        }
        return item;
      });
    } else {
      updated = [...normalizedIngredients, { name: cleanName, count: newCount }];
    }

    onIngredientsChange(updated);
    setNewIngredient('');
    setNewCount(1);
  };

  // Calculate total items count
  const totalItems = normalizedIngredients.reduce((sum, item) => sum + item.count, 0);

  // Construct full URL for labeled image
  const fullLabeledImageUrl = labeledImageUrl ? (import.meta.env.VITE_API_BASE_URL || '') + labeledImageUrl : null;

  return (
    <div className="card animate-slide-up">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary-100 dark:bg-primary-900 rounded-lg flex-shrink-0">
            <Apple className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Inventory & Ingredients
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {normalizedIngredients.length} unique items ({totalItems} total)
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2 self-end md:self-auto">
          {cacheHit && (
            <div className="badge badge-success flex items-center space-x-1">
              <CheckCircle className="w-4 h-4" />
              <span>Cached</span>
            </div>
          )}
          
          {fullLabeledImageUrl && (
            <button
              onClick={() => setShowLabeledImage(!showLabeledImage)}
              className="btn-secondary flex items-center space-x-2 text-sm py-1.5 px-3"
              title={showLabeledImage ? 'Hide labeled image' : 'View labeled image'}
            >
              {showLabeledImage ? (
                <>
                  <EyeOff className="w-4 h-4" />
                  <span className="hidden sm:inline">Hide Labels</span>
                </>
              ) : (
                <>
                  <Eye className="w-4 h-4" />
                  <span className="hidden sm:inline">View Labels</span>
                </>
              )}
            </button>
          )}

          {onRecalculate && (
            <button
              onClick={onRecalculate}
              disabled={isRecalculating || normalizedIngredients.length === 0}
              className="btn-primary flex items-center space-x-2 text-sm py-1.5 px-4 shadow-md bg-gradient-to-r from-primary-600 to-green-600 hover:from-primary-700 hover:to-green-700 transition-all duration-300"
            >
              <RotateCw className={`w-4 h-4 ${isRecalculating ? 'animate-spin' : ''}`} />
              <span>{isRecalculating ? 'Recalculating...' : 'Recalculate Recipes'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Labeled Image Display */}
      {showLabeledImage && fullLabeledImageUrl && (
        <div className="mb-6 animate-slide-up">
          <div className="relative rounded-lg overflow-hidden border-2 border-primary-200 dark:border-primary-700 shadow-lg">
            <img
              src={fullLabeledImageUrl}
              alt="Labeled ingredients"
              className="w-full h-auto"
              onError={(e) => {
                console.error('Failed to load labeled image');
                e.target.style.display = 'none';
              }}
            />
            <div className="absolute top-3 right-3 bg-black bg-opacity-60 text-white px-3 py-1 rounded-full text-xs font-medium flex items-center space-x-1">
              <ImageIcon className="w-3 h-3" />
              <span>AI Labeled</span>
            </div>
          </div>
        </div>
      )}

      {/* Interactive Add Form */}
      <form onSubmit={handleAddIngredient} className="flex items-center gap-2 mb-6 p-3 bg-gray-50 dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700">
        <div className="flex-1 relative">
          <input
            type="text"
            placeholder="Add new ingredient (e.g. spinach, cheese)..."
            value={newIngredient}
            onChange={(e) => setNewIngredient(e.target.value)}
            list="common-ingredients-list"
            className="w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-800 dark:text-gray-100"
          />
          <datalist id="common-ingredients-list">
            {commonIngredients.map((item, idx) => (
              <option key={idx} value={item} />
            ))}
          </datalist>
        </div>
        <div className="flex items-center bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-2 py-1">
          <button 
            type="button" 
            onClick={() => setNewCount(Math.max(1, newCount - 1))}
            className="text-gray-500 dark:text-gray-400 font-bold px-2 py-1 hover:bg-gray-100 dark:hover:bg-gray-600 rounded"
          >
            -
          </button>
          <span className="px-3 text-sm font-semibold text-gray-700 dark:text-gray-200 min-w-[20px] text-center">
            {newCount}
          </span>
          <button 
            type="button" 
            onClick={() => setNewCount(newCount + 1)}
            className="text-gray-500 dark:text-gray-400 font-bold px-2 py-1 hover:bg-gray-100 dark:hover:bg-gray-600 rounded"
          >
            +
          </button>
        </div>
        <button
          type="submit"
          disabled={!newIngredient.trim()}
          className="btn-primary p-2.5 rounded-lg flex items-center justify-center bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Plus className="w-5 h-5" />
        </button>
      </form>

      {/* Ingredients Grid */}
      {normalizedIngredients.length === 0 ? (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400 border-2 border-dashed border-gray-200 dark:border-gray-700 rounded-xl">
          No ingredients in inventory. Use the input field above to add some!
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {normalizedIngredients.map((ingredient, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-800/80 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm transition-all duration-200 hover:shadow-md hover:border-primary-300 dark:hover:border-primary-800"
            >
              <div className="flex flex-col min-w-0 pr-2">
                <span className="text-sm font-bold text-gray-800 dark:text-gray-100 capitalize truncate flex items-center gap-1.5">
                  {ingredient.name}
                  {getSpoilageRisk(ingredient.name) === 'high' && (
                    <span 
                      className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full text-[9px] font-bold bg-amber-100 text-amber-800 dark:bg-amber-950/40 dark:text-amber-400 border border-amber-200 dark:border-amber-900"
                      title="Perishable ingredient with higher risk of spoiling. Prioritize using it!"
                    >
                      <AlertTriangle className="w-2.5 h-2.5" />
                      <span>Use Soon</span>
                    </span>
                  )}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  Qty: {ingredient.count}
                </span>
              </div>
              
              <div className="flex items-center space-x-2 flex-shrink-0">
                {/* Quantity adjuster */}
                <div className="flex items-center bg-gray-100 dark:bg-gray-700 rounded-lg p-0.5 border border-gray-200 dark:border-gray-600">
                  <button
                    onClick={() => handleCountChange(ingredient.name, -1)}
                    className="text-xs font-bold text-gray-500 dark:text-gray-400 w-6 h-6 hover:bg-white dark:hover:bg-gray-600 rounded-md transition-colors"
                  >
                    -
                  </button>
                  <button
                    onClick={() => handleCountChange(ingredient.name, 1)}
                    className="text-xs font-bold text-gray-500 dark:text-gray-400 w-6 h-6 hover:bg-white dark:hover:bg-gray-600 rounded-md transition-colors"
                  >
                    +
                  </button>
                </div>

                {/* Delete button */}
                <button
                  onClick={() => handleDelete(ingredient.name)}
                  className="p-1.5 text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950/40 rounded-lg transition-colors"
                  title={`Delete ${ingredient.name}`}
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default IngredientsList;

// Made with Bob
