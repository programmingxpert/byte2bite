import React from 'react';
import { Leaf, TrendingUp, Gauge, Globe, Award } from 'lucide-react';

/**
 * MetricCard Component
 * Displays individual sustainability metric
 */
const MetricCard = ({ icon: Icon, title, value, subtitle, color = 'primary', darkMode }) => {
  const colorClasses = {
    primary: 'bg-primary-100 text-primary-600 dark:bg-primary-900 dark:text-primary-400',
    green: 'bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-400',
    blue: 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-400',
    orange: 'bg-orange-100 text-orange-600 dark:bg-orange-900 dark:text-orange-400',
  };

  return (
    <div className="card hover:shadow-xl transition-all duration-300 animate-scale-in">
      <div className="flex items-start space-x-4">
        <div className={`p-3 rounded-xl ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mb-1">{value}</p>
          {subtitle && (
            <p className="text-xs text-gray-500 dark:text-gray-400">{subtitle}</p>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * SustainabilityMetrics Component
 * Displays comprehensive sustainability analysis
 */
const SustainabilityMetrics = ({ sustainability, darkMode }) => {
  if (!sustainability) {
    return null;
  }

  const {
    ingredient_utilization,
    waste_reduction,
    sustainability: sustainabilityScore,
    co2_impact,
    sdg_alignment,
    summary,
  } = sustainability;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
          <Leaf className="w-6 h-6 text-green-600 dark:text-green-400" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Sustainability Analysis
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Environmental impact and waste reduction metrics
          </p>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          icon={TrendingUp}
          title="Ingredient Utilization"
          value={`${ingredient_utilization}%`}
          subtitle={`${summary.ingredients_used}/${summary.ingredients_available} ingredients used`}
          color="primary"
          darkMode={darkMode}
        />

        <MetricCard
          icon={Gauge}
          title="Waste Reduction Score"
          value={`${waste_reduction.score}/10`}
          subtitle={waste_reduction.explanation}
          color="green"
          darkMode={darkMode}
        />

        <MetricCard
          icon={Leaf}
          title="CO₂ Saved"
          value={`${co2_impact.net_co2_saved} kg`}
          subtitle={`≈ ${co2_impact.equivalent_km_driven} km driving`}
          color="blue"
          darkMode={darkMode}
        />

        <MetricCard
          icon={Globe}
          title="SDG 12 Alignment"
          value={`${sdg_alignment.sdg_score}/100`}
          subtitle={sdg_alignment.impact_level}
          color="orange"
          darkMode={darkMode}
        />
      </div>

      {/* Detailed Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sustainability Breakdown */}
        <div className="card">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
            <Award className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            <span>Sustainability Breakdown</span>
          </h3>
          
          <div className="space-y-4">
            {Object.entries(sustainabilityScore.breakdown).map(([key, value]) => {
              if (key === 'overall') return null;
              
              const label = key.split('_').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
              ).join(' ');
              
              const percentage = (value / 100) * 100;
              
              return (
                <div key={key}>
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="font-medium text-gray-700 dark:text-gray-300">{label}</span>
                    <span className="font-semibold text-gray-900 dark:text-white">{value}/100</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-primary-500 to-green-500 rounded-full transition-all duration-1000"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <span className="text-sm font-bold text-gray-700 dark:text-gray-300">Overall Score</span>
              <span className="text-xl font-bold text-primary-600 dark:text-primary-400">
                {sustainabilityScore.overall_score}/100
              </span>
            </div>
          </div>
        </div>

        {/* CO2 Impact Details */}
        <div className="card">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
            <Leaf className="w-5 h-5 text-green-600 dark:text-green-400" />
            <span>Carbon Footprint</span>
          </h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900 rounded-lg">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">CO₂ Saved from Waste</span>
              <span className="text-lg font-bold text-green-600 dark:text-green-400">
                {co2_impact.co2_saved_from_waste} kg
              </span>
            </div>

            <div className="flex items-center justify-between p-3 bg-orange-50 dark:bg-orange-900 rounded-lg">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">CO₂ from Cooking</span>
              <span className="text-lg font-bold text-orange-600 dark:text-orange-400">
                {co2_impact.co2_from_cooking} kg
              </span>
            </div>

            <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900 rounded-lg border-2 border-blue-200 dark:border-blue-700">
              <span className="text-sm font-bold text-gray-900 dark:text-white">Net CO₂ Saved</span>
              <span className="text-xl font-bold text-blue-600 dark:text-blue-400">
                {co2_impact.net_co2_saved} kg
              </span>
            </div>

            <div className="mt-4 p-4 bg-gradient-to-r from-blue-50 to-green-50 dark:from-blue-900 dark:to-green-900 rounded-lg border border-blue-200 dark:border-blue-700">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                <span className="font-semibold">Environmental Impact:</span> This is equivalent to 
                driving <span className="font-bold text-blue-600 dark:text-blue-400">{co2_impact.equivalent_km_driven} km</span> in 
                an average car. Great job reducing your carbon footprint! 🌍
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* SDG Alignment */}
      <div className="card bg-gradient-to-br from-blue-50 to-green-50 dark:from-blue-900 dark:to-green-900 border-2 border-blue-200 dark:border-blue-700">
        <div className="flex items-start space-x-4">
          <div className="p-3 bg-blue-100 dark:bg-blue-800 rounded-xl">
            <Globe className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
              UN SDG 12: Responsible Consumption and Production
            </h3>
            <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
              {sdg_alignment.description}
            </p>
            <div className="space-y-2">
              <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">Targets Addressed:</p>
              <ul className="space-y-1">
                {sdg_alignment.targets_addressed.map((target, index) => (
                  <li key={index} className="text-sm text-gray-700 dark:text-gray-300 flex items-start space-x-2">
                    <span className="text-green-600 dark:text-green-400 font-bold">✓</span>
                    <span>{target}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SustainabilityMetrics;

// Made with Bob
