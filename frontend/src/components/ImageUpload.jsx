import React, { useState, useRef } from 'react';
import { Upload, Image as ImageIcon, X, Leaf, Drumstick, Utensils } from 'lucide-react';

/**
 * ImageUpload Component
 * Handles image upload with drag-and-drop functionality and dietary preference selection
 */
const ImageUpload = ({ onImageSelect, disabled, dietaryPreference, onDietaryChange, darkMode }) => {
  const [dragActive, setDragActive] = useState(false);
  const [preview, setPreview] = useState(null);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB');
      return;
    }

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result);
    };
    reader.readAsDataURL(file);

    // Pass file to parent
    onImageSelect(file);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const clearImage = () => {
    setPreview(null);
    onImageSelect(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-full space-y-6">
      {/* Dietary Preference Selector */}
      <div className="card bg-gradient-to-br from-green-50 to-primary-50 dark:from-green-900 dark:to-primary-900">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center space-x-2">
          <Utensils className="w-4 h-4" />
          <span>Dietary Preference</span>
        </h3>
        <div className="grid grid-cols-3 gap-3">
          <button
            onClick={() => onDietaryChange('all')}
            disabled={disabled}
            className={`p-4 rounded-lg border-2 transition-all duration-200 ${
              dietaryPreference === 'all'
                ? 'border-primary-500 bg-primary-100 dark:bg-primary-900 shadow-md'
                : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 hover:border-primary-300 dark:hover:border-primary-500'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            <div className="flex flex-col items-center space-y-2">
              <Utensils className={`w-6 h-6 ${
                dietaryPreference === 'all' ? 'text-primary-600 dark:text-primary-400' : 'text-gray-500 dark:text-gray-400'
              }`} />
              <span className={`text-sm font-medium ${
                dietaryPreference === 'all' ? 'text-primary-700 dark:text-primary-300' : 'text-gray-700 dark:text-gray-300'
              }`}>
                All Recipes
              </span>
            </div>
          </button>

          <button
            onClick={() => onDietaryChange('vegetarian')}
            disabled={disabled}
            className={`p-4 rounded-lg border-2 transition-all duration-200 ${
              dietaryPreference === 'vegetarian'
                ? 'border-green-500 bg-green-100 dark:bg-green-900 shadow-md'
                : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 hover:border-green-300 dark:hover:border-green-500'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            <div className="flex flex-col items-center space-y-2">
              <Leaf className={`w-6 h-6 ${
                dietaryPreference === 'vegetarian' ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'
              }`} />
              <span className={`text-sm font-medium ${
                dietaryPreference === 'vegetarian' ? 'text-green-700 dark:text-green-300' : 'text-gray-700 dark:text-gray-300'
              }`}>
                Vegetarian
              </span>
            </div>
          </button>

          <button
            onClick={() => onDietaryChange('non-vegetarian')}
            disabled={disabled}
            className={`p-4 rounded-lg border-2 transition-all duration-200 ${
              dietaryPreference === 'non-vegetarian'
                ? 'border-orange-500 bg-orange-100 dark:bg-orange-900 shadow-md'
                : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 hover:border-orange-300 dark:hover:border-orange-500'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            <div className="flex flex-col items-center space-y-2">
              <Drumstick className={`w-6 h-6 ${
                dietaryPreference === 'non-vegetarian' ? 'text-orange-600 dark:text-orange-400' : 'text-gray-500 dark:text-gray-400'
              }`} />
              <span className={`text-sm font-medium ${
                dietaryPreference === 'non-vegetarian' ? 'text-orange-700 dark:text-orange-300' : 'text-gray-700 dark:text-gray-300'
              }`}>
                Non-Vegetarian
              </span>
            </div>
          </button>
        </div>
      </div>

      {/* Image Upload Area */}
      {!preview ? (
        <div
          className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${
            dragActive
              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900'
              : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 dark:hover:border-primary-500 bg-white dark:bg-gray-800'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={!disabled ? handleClick : undefined}
        >
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept="image/*"
            onChange={handleChange}
            disabled={disabled}
          />

          <div className="flex flex-col items-center space-y-4">
            <div className={`p-4 rounded-full ${
              dragActive ? 'bg-primary-100 dark:bg-primary-800' : 'bg-gray-100 dark:bg-gray-700'
            }`}>
              <Upload className={`w-12 h-12 ${
                dragActive ? 'text-primary-600 dark:text-primary-400' : 'text-gray-400 dark:text-gray-500'
              }`} />
            </div>

            <div>
              <p className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-1">
                {dragActive ? 'Drop your image here' : 'Upload an image'}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Drag and drop or click to browse
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
                Supports: JPG, PNG (Max 10MB)
              </p>

              <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900 rounded-lg max-w-sm mx-auto text-left">
                <p className="text-xs font-semibold text-blue-800 dark:text-blue-300 flex items-center gap-1.5 mb-1">
                  💡 Tips for best results:
                </p>
                <ul className="list-disc list-inside text-[11px] text-blue-700 dark:text-blue-400 space-y-0.5">
                  <li>Make sure the photo is clear and well-lit.</li>
                  <li>Show the food items clearly without heavy overlap.</li>
                  <li>Capture the ingredients from a top-down angle.</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="relative card animate-scale-in">
          <button
            onClick={clearImage}
            disabled={disabled}
            className="absolute top-2 right-2 p-2 bg-red-500 hover:bg-red-600 text-white rounded-full transition-all duration-200 transform hover:scale-110 disabled:opacity-50 disabled:cursor-not-allowed z-10"
            title="Remove image"
          >
            <X className="w-5 h-5" />
          </button>

          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <ImageIcon className="w-8 h-8 text-primary-600 dark:text-primary-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                Image uploaded successfully
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Ready for analysis
              </p>
            </div>
          </div>

          <div className="mt-4 rounded-lg overflow-hidden">
            <img
              src={preview}
              alt="Preview"
              className="w-full h-64 object-cover"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;

// Made with Bob
