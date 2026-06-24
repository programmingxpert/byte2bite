import React from 'react';
import { X, CheckCircle2, XCircle, Clock, Users, ChefHat, Leaf, Drumstick, TrendingUp } from 'lucide-react';

/**
 * RecipeDetailsModal Component
 * Displays full recipe information in a modal overlay
 */
const RecipeDetailsModal = ({ recipe, isOpen, onClose, onAddToShoppingList }) => {
  if (!isOpen || !recipe) return null;

  const { 
    name, 
    score, 
    matched, 
    missing, 
    cuisine, 
    difficulty, 
    time, 
    servings, 
    description,
    dietary,
    ingredients_used,
    utilization
  } = recipe;

  // Close modal when clicking outside
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  // Get difficulty color
  const getDifficultyColor = (diff) => {
    switch (diff?.toLowerCase()) {
      case 'easy': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'hard': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 animate-fade-in"
      onClick={handleBackdropClick}
    >
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto animate-slide-up">
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 flex items-start justify-between z-10">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <div className="p-2 bg-primary-100 dark:bg-primary-900 rounded-lg">
                <ChefHat className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                {name}
              </h2>
            </div>
            
            {/* Badges */}
            <div className="flex flex-wrap gap-2">
              {/* Dietary Badge */}
              <div className={`flex items-center space-x-1 px-3 py-1 rounded-full text-sm font-medium ${
                dietary === 'vegetarian'
                  ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                  : 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300'
              }`}>
                {dietary === 'vegetarian' ? (
                  <>
                    <Leaf className="w-4 h-4" />
                    <span>Vegetarian</span>
                  </>
                ) : (
                  <>
                    <Drumstick className="w-4 h-4" />
                    <span>Non-Veg</span>
                  </>
                )}
              </div>

              {/* Cuisine Badge */}
              <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full text-sm font-medium">
                {cuisine}
              </span>

              {/* Difficulty Badge */}
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(difficulty)}`}>
                {difficulty}
              </span>
            </div>
          </div>

          {/* Close Button */}
          <button
            onClick={onClose}
            className="ml-4 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            aria-label="Close modal"
          >
            <X className="w-6 h-6 text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Match Score */}
          <div className="bg-gradient-to-br from-primary-50 to-green-50 dark:from-primary-900 dark:to-green-900 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                  Recipe Match
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  {ingredients_used} of your ingredients used
                </p>
              </div>
              <div className="text-right">
                <div className={`text-4xl font-bold ${
                  score >= 80 ? 'text-green-600 dark:text-green-400' : 
                  score >= 60 ? 'text-yellow-600 dark:text-yellow-400' : 
                  'text-orange-600 dark:text-orange-400'
                }`}>
                  {score}%
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">Match Score</div>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-1000 ${
                  score >= 80 ? 'bg-green-500' : 
                  score >= 60 ? 'bg-yellow-500' : 
                  'bg-orange-500'
                }`}
                style={{ width: `${score}%` }}
              />
            </div>

            {/* Utilization */}
            <div className="mt-3 flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-300">
              <TrendingUp className="w-4 h-4" />
              <span>Using {utilization}% of your available ingredients</span>
            </div>
          </div>

          {/* Description */}
          {description && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                About This Recipe
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                {description}
              </p>
            </div>
          )}

          {/* Recipe Info */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center space-x-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <Clock className="w-5 h-5 text-primary-600 dark:text-primary-400" />
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Cooking Time</p>
                <p className="font-semibold text-gray-900 dark:text-white">{time}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <Users className="w-5 h-5 text-primary-600 dark:text-primary-400" />
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Servings</p>
                <p className="font-semibold text-gray-900 dark:text-white">{servings} people</p>
              </div>
            </div>
          </div>

          {/* Ingredients You Have */}
          {matched && matched.length > 0 && (
            <div>
              <div className="flex items-center space-x-2 mb-3">
                <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-400" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Ingredients You Have ({matched.length})
                </h3>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {matched.map((ingredient, index) => (
                  <div
                    key={index}
                    className="flex items-center space-x-2 p-3 bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700 rounded-lg"
                  >
                    <CheckCircle2 className="w-4 h-4 text-green-600 dark:text-green-400 flex-shrink-0" />
                    <span className="text-sm text-green-800 dark:text-green-200 capitalize">
                      {ingredient}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Missing Ingredients */}
          {missing && missing.length > 0 && (
            <div>
              <div className="flex items-center space-x-2 mb-3">
                <XCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Ingredients You Need ({missing.length})
                </h3>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {missing.map((ingredient, index) => (
                  <div
                    key={index}
                    className="flex items-center space-x-2 p-3 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg"
                  >
                    <XCircle className="w-4 h-4 text-red-600 dark:text-red-400 flex-shrink-0" />
                    <span className="text-sm text-red-800 dark:text-red-200 capitalize">
                      {ingredient}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={onClose}
              className="flex-1 btn-secondary"
            >
              Close
            </button>
            <button
              className="flex-1 btn-primary"
              onClick={() => {
                if (onAddToShoppingList && missing) {
                  onAddToShoppingList(missing);
                }
                onClose();
              }}
              disabled={!missing || missing.length === 0}
            >
              Add Missing Items to List
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecipeDetailsModal;

// Made with Bob