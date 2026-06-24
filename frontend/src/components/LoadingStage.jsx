import React from 'react';
import { Loader2, CheckCircle2, Circle } from 'lucide-react';

/**
 * LoadingStage Component
 * Displays the current processing stage with visual indicators
 */
const LoadingStage = ({ stage, message, progress, isActive, isComplete, darkMode }) => {
  return (
    <div
      className={`stage-indicator ${
        isActive ? 'stage-active' : isComplete ? 'stage-complete' : 'stage-pending'
      } animate-fade-in`}
    >
      <div className="flex-shrink-0">
        {isComplete ? (
          <CheckCircle2 className="w-6 h-6 text-green-600 dark:text-green-400" />
        ) : isActive ? (
          <Loader2 className="w-6 h-6 text-primary-600 dark:text-primary-400 animate-spin" />
        ) : (
          <Circle className="w-6 h-6 text-gray-400 dark:text-gray-500" />
        )}
      </div>
      
      <div className="flex-1 min-w-0">
        <p className={`font-medium ${
          isActive ? 'text-primary-700 dark:text-primary-300' : 
          isComplete ? 'text-green-700 dark:text-green-300' : 
          'text-gray-500 dark:text-gray-400'
        }`}>
          {message}
        </p>
        
        {isActive && progress > 0 && (
          <div className="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
            <div
              className="progress-bar"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
      </div>
      
      {isActive && progress > 0 && (
        <div className="flex-shrink-0 ml-4">
          <span className="text-sm font-semibold text-primary-600 dark:text-primary-400">
            {progress}%
          </span>
        </div>
      )}
    </div>
  );
};

/**
 * LoadingStages Component
 * Manages and displays all processing stages
 */
const LoadingStages = ({ currentStage, progress, darkMode }) => {
  const stages = [
    { id: 'upload', label: 'Uploading image...' },
    { id: 'detection', label: 'Detecting ingredients with AI...' },
    { id: 'matching', label: 'Matching recipes...' },
    { id: 'sustainability', label: 'Calculating sustainability metrics...' },
    { id: 'ai', label: 'Generating AI recommendations...' },
  ];

  const currentIndex = stages.findIndex(s => s.id === currentStage);

  return (
    <div className="space-y-3">
      {stages.map((stage, index) => (
        <LoadingStage
          key={stage.id}
          stage={stage.id}
          message={stage.label}
          progress={index === currentIndex ? progress : 0}
          isActive={index === currentIndex}
          isComplete={index < currentIndex}
          darkMode={darkMode}
        />
      ))}
    </div>
  );
};

export { LoadingStage, LoadingStages };
export default LoadingStages;

// Made with Bob
