import React, { useState } from 'react';
import { ChefHat, CheckCircle2, XCircle, Target, TrendingUp, Leaf, Drumstick, ChevronDown, ChevronUp, BarChart3 } from 'lucide-react';
import RecipeDetailsModal from './RecipeDetailsModal';

/**
 * RecipeCard Component
 * Displays individual recipe with match details and dietary badge
 * Adjusts visual emphasis based on sorting mode
 */
const RecipeCard = ({ recipe, rank, isTopPick, darkMode, onClick, sortBy = 'match_percentage' }) => {
  const { name, score, matched, missing, target, dietary, utilization, quantity_info, ingredients_used } = recipe;

  // Check if we have sufficient quantities for all matched ingredients
  const hasQuantityInfo = quantity_info && Object.keys(quantity_info).length > 0;
  const allSufficient = hasQuantityInfo && Object.values(quantity_info).every(info => info.sufficient);

  return (
    <div
      onClick={onClick}
      className={`card hover:shadow-2xl transition-all duration-300 cursor-pointer ${
        isTopPick ? 'ring-2 ring-primary-500 bg-gradient-to-br from-white to-primary-50 dark:from-gray-800 dark:to-primary-900' : ''
      } animate-slide-up`}
    >
      {isTopPick && (
        <div className="absolute -top-3 -right-3 bg-primary-600 text-white px-4 py-1 rounded-full text-sm font-bold shadow-lg flex items-center space-x-1">
          <TrendingUp className="w-4 h-4" />
          <span>Top Pick</span>
        </div>
      )}

      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-3 rounded-xl ${
            isTopPick ? 'bg-primary-100 dark:bg-primary-800' : 'bg-gray-100 dark:bg-gray-700'
          }`}>
            <ChefHat className={`w-6 h-6 ${
              isTopPick ? 'text-primary-600 dark:text-primary-400' : 'text-gray-600 dark:text-gray-400'
            }`} />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              {rank && (
                <span className="text-sm font-bold text-gray-400 dark:text-gray-500">
                  #{rank}
                </span>
              )}
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                {name}
              </h3>
            </div>
            <div className="flex items-center space-x-2 mt-1">
              {/* Dietary Badge */}
              {dietary && (
                <div className={`flex items-center space-x-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                  dietary === 'vegetarian'
                    ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                    : 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300'
                }`}>
                  {dietary === 'vegetarian' ? (
                    <>
                      <Leaf className="w-3 h-3" />
                      <span>Vegetarian</span>
                    </>
                  ) : (
                    <>
                      <Drumstick className="w-3 h-3" />
                      <span>Non-Veg</span>
                    </>
                  )}
                </div>
              )}
              {/* Target Badge */}
              {target && target.toLowerCase() !== 'general' && (
                <div className="flex items-center space-x-1">
                  <Target className="w-4 h-4 text-orange-500 dark:text-orange-400" />
                  <span className="text-xs text-orange-600 dark:text-orange-400 font-medium">
                    {target}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="text-right">
          {sortBy === 'ingredients_used' ? (
            // Emphasize ingredients used when sorted by ingredients
            <>
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {ingredients_used}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 font-semibold">Ingredients</div>
              <div className="mt-1">
                <div className={`text-sm font-semibold ${
                  utilization >= 50 ? 'text-green-600 dark:text-green-400' : 'text-gray-600 dark:text-gray-400'
                }`}>
                  {utilization}%
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">Utilized</div>
              </div>
              <div className="mt-1">
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {score}%
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">Match</div>
              </div>
            </>
          ) : (
            // Emphasize match percentage when sorted by match (default)
            <>
              <div className={`text-2xl font-bold ${
                score >= 80 ? 'text-green-600 dark:text-green-400' :
                score >= 60 ? 'text-yellow-600 dark:text-yellow-400' :
                'text-orange-600 dark:text-orange-400'
              }`}>
                {score}%
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 font-semibold">Match</div>
              {utilization !== undefined && (
                <div className="mt-1">
                  <div className={`text-sm font-semibold ${
                    utilization >= 50 ? 'text-blue-600 dark:text-blue-400' : 'text-gray-600 dark:text-gray-400'
                  }`}>
                    {utilization}%
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Used</div>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      <div className="space-y-3">
        {/* Quantity Sufficiency Badge */}
        {hasQuantityInfo && (
          <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg ${
            allSufficient
              ? 'bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800'
              : 'bg-yellow-50 dark:bg-yellow-900/30 border border-yellow-200 dark:border-yellow-800'
          }`}>
            <CheckCircle2 className={`w-4 h-4 ${
              allSufficient ? 'text-green-600 dark:text-green-400' : 'text-yellow-600 dark:text-yellow-400'
            }`} />
            <span className={`text-sm font-medium ${
              allSufficient
                ? 'text-green-700 dark:text-green-300'
                : 'text-yellow-700 dark:text-yellow-300'
            }`}>
              {allSufficient ? '✓ Enough ingredients' : 'Check quantities needed'}
            </span>
          </div>
        )}

        {/* Matched Ingredients */}
        {matched && matched.length > 0 && (
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <CheckCircle2 className="w-4 h-4 text-green-600 dark:text-green-400" />
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                You have ({matched.length})
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {matched.slice(0, 5).map((ingredient, index) => {
                const quantityData = quantity_info?.[ingredient];
                return (
                  <span
                    key={index}
                    className="badge badge-success text-xs flex items-center space-x-1"
                  >
                    <span>{ingredient}</span>
                    {quantityData && quantityData.user_has > 1 && (
                      <span className="font-bold">×{quantityData.user_has}</span>
                    )}
                  </span>
                );
              })}
              {matched.length > 5 && (
                <span className="text-xs text-gray-500 dark:text-gray-400 self-center">
                  +{matched.length - 5} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Missing Ingredients */}
        {missing && missing.length > 0 && (
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <XCircle className="w-4 h-4 text-red-600 dark:text-red-400" />
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                You need ({missing.length})
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {missing.slice(0, 5).map((ingredient, index) => (
                <span
                  key={index}
                  className="badge badge-warning text-xs"
                >
                  {ingredient}
                </span>
              ))}
              {missing.length > 5 && (
                <span className="text-xs text-gray-500 dark:text-gray-400 self-center">
                  +{missing.length - 5} more
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 mb-2">
          <span>Ingredient Match</span>
          <span className="font-semibold">{score}%</span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-1000 ${
              score >= 80 ? 'bg-green-500' : score >= 60 ? 'bg-yellow-500' : 'bg-orange-500'
            }`}
            style={{ width: `${score}%` }}
          />
        </div>
      </div>

      {/* Click to view details hint */}
      <div className="mt-3 text-center text-xs text-gray-500 dark:text-gray-400">
        Click to view full recipe details
      </div>
    </div>
  );
};

/**
 * RecipesList Component
 * Displays all matched recipes with show more functionality and sorting controls
 */
const RecipesList = ({ recipes, darkMode, sortBy, onSortChange, onAddToShoppingList }) => {
  const [showAll, setShowAll] = useState(false);
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  if (!recipes || recipes.length === 0) {
    return null;
  }

  const displayedRecipes = showAll ? recipes : recipes.slice(0, 5);
  const hasMore = recipes.length > 5;

  const handleRecipeClick = (recipe) => {
    setSelectedRecipe(recipe);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedRecipe(null);
  };

  return (
    <>
      <div className="space-y-6 animate-fade-in">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
              <ChefHat className="w-6 h-6 text-orange-600 dark:text-orange-400" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Recipe Matches
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {recipes.length} recipe{recipes.length !== 1 ? 's' : ''} found
                {!showAll && hasMore && ` (showing ${displayedRecipes.length})`}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {/* Sorting Toggle */}
            <div className="flex items-center space-x-2 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
              <button
                onClick={() => onSortChange('match_percentage')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                  sortBy === 'match_percentage'
                    ? 'bg-white dark:bg-gray-700 text-primary-600 dark:text-primary-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                }`}
                title="Sort by match percentage - shows recipes you can make most completely"
              >
                <Target className="w-4 h-4" />
                <span>Best Match</span>
              </button>
              <button
                onClick={() => onSortChange('ingredients_used')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                  sortBy === 'ingredients_used'
                    ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                }`}
                title="Sort by ingredients used - shows recipes using most of your ingredients"
              >
                <BarChart3 className="w-4 h-4" />
                <span>Most Ingredients</span>
              </button>
            </div>

            {/* Show More/Less Button */}
            {hasMore && (
              <button
                onClick={() => setShowAll(!showAll)}
                className="btn-secondary flex items-center space-x-2"
              >
                {showAll ? (
                  <>
                    <ChevronUp className="w-4 h-4" />
                    <span>Show Less</span>
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-4 h-4" />
                    <span>Show More ({recipes.length - 5})</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {displayedRecipes.map((recipe, index) => (
            <RecipeCard
              key={index}
              recipe={recipe}
              rank={index + 1}
              isTopPick={index === 0}
              darkMode={darkMode}
              onClick={() => handleRecipeClick(recipe)}
              sortBy={sortBy}
            />
          ))}
        </div>

        {/* Show All Button at Bottom */}
        {hasMore && !showAll && (
          <div className="text-center pt-4">
            <button
              onClick={() => setShowAll(true)}
              className="btn-primary flex items-center space-x-2 mx-auto"
            >
              <ChevronDown className="w-4 h-4" />
              <span>Show All {recipes.length} Recipes</span>
            </button>
          </div>
        )}
      </div>

      {/* Recipe Details Modal */}
      <RecipeDetailsModal
        recipe={selectedRecipe}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onAddToShoppingList={onAddToShoppingList}
      />
    </>
  );
};

export { RecipeCard, RecipesList };
export default RecipesList;

// Made with Bob
