import React, { useState } from 'react';
import { ShoppingBag, X, Plus, Check, Trash2 } from 'lucide-react';

/**
 * ShoppingList Component
 * Displays a collapsible slide-out drawer containing missing recipe ingredients 
 * and custom items to purchase.
 */
const ShoppingList = ({ items, isOpen, onClose, onClear, onRemoveItem, onAddItem, onToggleChecked }) => {
  const [customItem, setCustomItem] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!customItem.trim()) return;
    onAddItem(customItem.trim());
    setCustomItem('');
  };

  const checkedCount = items.filter(item => item.checked).length;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden animate-fade-in">
      {/* Backdrop overlay */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-40 transition-opacity" 
        onClick={onClose}
      />

      <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md transform transition-all duration-300 ease-in-out bg-white dark:bg-gray-800 shadow-2xl flex flex-col h-full rounded-l-2xl border-l border-gray-200 dark:border-gray-700">
          {/* Header */}
          <div className="px-6 py-5 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/60 rounded-xl">
                <ShoppingBag className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Shopping List</h2>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {checkedCount} of {items.length} items checked
                </p>
              </div>
            </div>
            
            <button 
              onClick={onClose}
              className="p-2 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Add custom item */}
          <form onSubmit={handleSubmit} className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center gap-2">
            <input
              type="text"
              placeholder="Add item (e.g. eggs, garlic)..."
              value={customItem}
              onChange={(e) => setCustomItem(e.target.value)}
              className="flex-1 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-800 dark:text-gray-100"
            />
            <button
              type="submit"
              disabled={!customItem.trim()}
              className="p-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50 transition-colors"
            >
              <Plus className="w-4 h-4" />
            </button>
          </form>

          {/* Items List */}
          <div className="flex-1 overflow-y-auto p-6 space-y-3">
            {items.length === 0 ? (
              <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                <ShoppingBag className="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-3" />
                <p className="text-sm font-semibold">Your shopping list is empty</p>
                <p className="text-xs mt-1 text-gray-400">Add missing recipe items or input items above.</p>
              </div>
            ) : (
              items.map((item, idx) => (
                <div 
                  key={idx}
                  onClick={() => onToggleChecked(idx)}
                  className={`flex items-center justify-between p-3 rounded-xl border cursor-pointer select-none transition-all duration-200 ${
                    item.checked 
                      ? 'bg-gray-50 dark:bg-gray-800/40 border-gray-200 dark:border-gray-700 opacity-60' 
                      : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-700 shadow-sm'
                  }`}
                >
                  <div className="flex items-center space-x-3 min-w-0">
                    <div className={`w-5 h-5 rounded-md flex items-center justify-center border transition-all duration-200 ${
                      item.checked 
                        ? 'bg-blue-600 border-blue-600 text-white' 
                        : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700'
                    }`}>
                      {item.checked && <Check className="w-3.5 h-3.5" />}
                    </div>
                    <div className="min-w-0">
                      <span className={`text-sm font-medium capitalize block truncate text-gray-800 dark:text-gray-200 ${
                        item.checked ? 'line-through text-gray-400 dark:text-gray-500' : ''
                      }`}>
                        {item.name}
                      </span>
                      {item.note && (
                        <span className="text-[10px] text-gray-500 dark:text-gray-400 block truncate mt-0.5">
                          {item.note}
                        </span>
                      )}
                    </div>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onRemoveItem(idx);
                    }}
                    className="p-1.5 text-gray-400 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/20 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          {items.length > 0 && (
            <div className="p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/60 rounded-b-2xl">
              <button
                onClick={onClear}
                className="w-full flex items-center justify-center space-x-2 py-3 border border-red-200 dark:border-red-800 hover:bg-red-50 dark:hover:bg-red-950/20 text-red-600 dark:text-red-400 font-semibold rounded-xl text-sm transition-all duration-200"
              >
                <Trash2 className="w-4 h-4" />
                <span>Clear All Checked</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ShoppingList;

// Made with Bob
