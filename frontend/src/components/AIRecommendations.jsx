import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, Brain, Lightbulb, Send, MessageSquare, Loader2, Bot } from 'lucide-react';
import { chatWithChef } from '../utils/api';

/**
 * AIRecommendations Component
 * Displays Granite AI-generated recipe recommendations, sustainability tips,
 * and an interactive AI Chef Chat widget.
 */
const AIRecommendations = ({ recommendation, tips, ingredients, recipeName, darkMode }) => {
  const [chatHistory, setChatHistory] = useState([]);
  const [message, setMessage] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);
  const chatEndRef = useRef(null);

  // Scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isChatLoading]);

  if (!recommendation && !tips) {
    return null;
  }

  // Parse the recommendation text into sections
  const parseRecommendation = (text) => {
    if (!text) return {};
    const sections = {};
    const lines = text.split('\n');
    let currentSection = 'general';
    let currentContent = [];

    lines.forEach(line => {
      const trimmed = line.trim();
      if (!trimmed) return;

      // Check if line is a section header (e.g., "Recipe Name: Classic Lemon Rice")
      if (trimmed.includes(':') && !trimmed.startsWith('-') && !trimmed.match(/^\d+\./)) {
        if (currentContent.length > 0) {
          sections[currentSection] = currentContent.join('\n');
        }
        const [header, ...content] = trimmed.split(':');
        currentSection = header.trim().toLowerCase().replace(/\s+/g, '_');
        currentContent = content.length > 0 ? [content.join(':').trim()] : [];
      } else {
        currentContent.push(trimmed);
      }
    });

    if (currentContent.length > 0) {
      sections[currentSection] = currentContent.join('\n');
    }

    return sections;
  };

  const sections = recommendation ? parseRecommendation(recommendation) : {};

  const handleSendMessage = async (e) => {
    e.preventDefault();
    const cleanMsg = message.trim();
    if (!cleanMsg || isChatLoading) return;

    // Add user message to history
    const userMessage = { role: 'user', content: cleanMsg };
    const updatedHistory = [...chatHistory, userMessage];
    setChatHistory(updatedHistory);
    setMessage('');
    setIsChatLoading(true);

    try {
      const ingredientNames = ingredients ? ingredients.map(i => typeof i === 'string' ? i : i.name) : [];
      // Call chat API
      const result = await chatWithChef(cleanMsg, chatHistory, ingredientNames, recipeName);
      
      // Add chef response to history
      setChatHistory(prev => [...prev, { role: 'assistant', content: result.response }]);
    } catch (err) {
      console.error('Chat error:', err);
      setChatHistory(prev => [...prev, { 
        role: 'assistant', 
        content: "I'm sorry, I had trouble connecting. Please check if Ollama is running and try again!" 
      }]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setMessage(suggestion);
  };

  const suggestions = [
    `How can I modify this recipe?`,
    "What substitutes can I use?",
    "Give me step-by-step instructions",
    "How should I store leftovers?"
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* AI Header */}
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
          <Brain className="w-6 h-6 text-purple-600 dark:text-purple-400" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            AI recommendations
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Powered by IBM Granite AI
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        {/* Recommendation Cards */}
        <div className="space-y-6">
          {recommendation && (
            <div className="card bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/40 dark:to-blue-900/40 border-2 border-purple-200 dark:border-purple-800 shadow-lg">
              <div className="flex items-start space-x-3 mb-4">
                <Sparkles className="w-6 h-6 text-purple-600 dark:text-purple-400 flex-shrink-0 mt-1" />
                <div className="flex-1 min-w-0">
                  <h3 className="text-xl font-extrabold text-gray-950 dark:text-white mb-4">
                    {sections.recipe_name || recipeName || 'Recipe Recommendation'}
                  </h3>

                  {/* Reason */}
                  {sections.reason && (
                    <div className="mb-4 p-4 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-purple-100/50 dark:border-purple-900/50">
                      <p className="text-xs font-bold text-purple-700 dark:text-purple-400 uppercase tracking-wide mb-1">Why this recipe?</p>
                      <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{sections.reason}</p>
                    </div>
                  )}

                  {/* Missing Ingredients */}
                  {sections.missing_ingredients && (
                    <div className="mb-4 p-4 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-purple-100/50 dark:border-purple-900/50">
                      <p className="text-xs font-bold text-purple-700 dark:text-purple-400 uppercase tracking-wide mb-1">Missing Ingredients</p>
                      <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{sections.missing_ingredients}</p>
                    </div>
                  )}

                  {/* Waste Reduction Score */}
                  {sections.waste_reduction_score && (
                    <div className="mb-4 p-4 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-purple-100/50 dark:border-purple-900/50">
                      <p className="text-xs font-bold text-purple-700 dark:text-purple-400 uppercase tracking-wide mb-1">Waste Reduction Impact</p>
                      <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{sections.waste_reduction_score}</p>
                    </div>
                  )}

                  {/* Cooking Instructions */}
                  {sections.cooking_instructions && (
                    <div className="p-4 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-purple-100/50 dark:border-purple-900/50">
                      <p className="text-xs font-bold text-purple-700 dark:text-purple-400 uppercase tracking-wide mb-3">Cooking Instructions</p>
                      <div className="text-sm text-gray-700 dark:text-gray-300 space-y-2.5">
                        {sections.cooking_instructions.split('\n').map((instruction, index) => {
                          const trimmed = instruction.trim();
                          if (!trimmed) return null;
                          return (
                            <div key={index} className="flex items-start space-x-2.5">
                              <span className="font-extrabold text-purple-600 dark:text-purple-400 flex-shrink-0 mt-0.5">
                                {trimmed.match(/^\d+\./) ? '' : '•'}
                              </span>
                              <span className="leading-relaxed">{trimmed}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* Fallback: Display raw text if parsing fails */}
                  {Object.keys(sections).length === 0 && (
                    <div className="p-4 bg-white dark:bg-gray-800 rounded-xl">
                      <pre className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap font-sans leading-relaxed">
                        {recommendation}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Sustainability Tips */}
          {tips && (
            <div className="card bg-gradient-to-br from-green-50 to-yellow-50 dark:from-green-900/30 dark:to-yellow-900/30 border-2 border-green-200 dark:border-green-800/80 shadow-lg">
              <div className="flex items-start space-x-3">
                <Lightbulb className="w-6 h-6 text-green-600 dark:text-green-400 flex-shrink-0 mt-1" />
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-3">
                    Sustainability Tips
                  </h3>
                  <div className="space-y-2">
                    {tips.split('\n').map((tip, index) => {
                      const trimmed = tip.trim();
                      if (!trimmed) return null;
                      return (
                        <div key={index} className="flex items-start space-x-2 p-3 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-green-100/30 dark:border-green-900/30">
                          <span className="text-green-600 dark:text-green-400 font-bold flex-shrink-0">✓</span>
                          <p className="text-sm text-gray-700 dark:text-gray-300">{trimmed.replace(/^[•\-]\s*/, '')}</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Interactive Chatbot */}
        <div className="card border border-purple-200 dark:border-gray-700 flex flex-col h-[520px] bg-white dark:bg-gray-800 shadow-xl overflow-hidden rounded-2xl">
          {/* Chat Header */}
          <div className="p-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white flex items-center space-x-3">
            <Bot className="w-6 h-6" />
            <div>
              <h3 className="font-bold text-sm sm:text-base">AI Kitchen Companion</h3>
              <p className="text-[10px] text-purple-200">Conversing with Chef Granite</p>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900/50">
            {chatHistory.length === 0 ? (
              <div className="text-center py-8 space-y-4">
                <MessageSquare className="w-12 h-12 mx-auto text-gray-300 dark:text-gray-700" />
                <div className="space-y-1">
                  <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">Ask the Chef anything!</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 max-w-xs mx-auto px-4">
                    Get custom revisions, substitution suggestions, or step-by-step recipes based on your ingredients.
                  </p>
                </div>
                
                {/* Suggestions Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 max-w-sm mx-auto">
                  {suggestions.map((sug, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSuggestionClick(sug)}
                      className="text-left p-2.5 bg-white dark:bg-gray-800 hover:bg-purple-50 dark:hover:bg-purple-950/20 hover:border-purple-300 dark:hover:border-purple-800 border border-gray-200 dark:border-gray-700 rounded-xl text-xs font-medium text-gray-700 dark:text-gray-300 shadow-sm transition-all"
                    >
                      {sug}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              chatHistory.map((msg, idx) => (
                <div 
                  key={idx} 
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-sm text-sm leading-relaxed ${
                    msg.role === 'user' 
                      ? 'bg-purple-600 text-white rounded-br-none' 
                      : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border border-gray-100 dark:border-gray-700 rounded-bl-none'
                  }`}>
                    {msg.content}
                  </div>
                </div>
              ))
            )}
            
            {isChatLoading && (
              <div className="flex justify-start">
                <div className="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl rounded-bl-none px-4 py-3 shadow-sm flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 text-purple-600 dark:text-purple-400 animate-spin" />
                  <span className="text-xs text-gray-500 dark:text-gray-400">Chef is thinking...</span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input Area */}
          <form onSubmit={handleSendMessage} className="p-3 border-t border-gray-200 dark:border-gray-700 flex items-center gap-2 bg-white dark:bg-gray-800">
            <input
              type="text"
              placeholder="Ask for variations, step instructions, storage tips..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              disabled={isChatLoading}
              className="flex-1 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 text-gray-800 dark:text-gray-100 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!message.trim() || isChatLoading}
              className="p-3 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white rounded-xl transition-all duration-200 flex items-center justify-center shadow-md disabled:cursor-not-allowed"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>

      {/* Note about Granite */}
      <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
        <p className="text-xs text-gray-600 dark:text-gray-400">
          <span className="font-semibold">Powered by IBM Granite AI</span> - 
          Advanced language model for sustainable cooking recommendations
        </p>
      </div>
    </div>
  );
};

export default AIRecommendations;

// Made with Bob
