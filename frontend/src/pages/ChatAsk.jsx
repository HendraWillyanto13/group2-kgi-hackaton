import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { generateReply } from '../lib/api';

/**
 * ChatAsk Component - A conversational chatbot interface
 * 
 * Features:
 * - Text input with submit button for user questions
 * - Maintains conversation history with context preservation
 * - Visual differentiation between user and bot messages
 * - Auto-scroll to latest messages
 * - Clear input after submission
 */
const ChatAsk = () => {
  // State for storing conversation history
  const [messages, setMessages] = useState([]);
  const [currentInput, setCurrentInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Ref for auto-scrolling to bottom
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input on component mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  /**
   * Handle form submission - add user message and get bot reply
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate input
    if (!currentInput.trim() || isLoading) {
      return;
    }

    const userMessage = { role: 'user', content: currentInput.trim() };
    const updatedMessages = [...messages, userMessage];
    
    // Update state with user message
    setMessages(updatedMessages);
    setCurrentInput('');
    setIsLoading(true);
    setError(null);

    try {
      // Call API with full message history including the new question
      const response = await generateReply(updatedMessages);
      
      // Add bot response to conversation
      const botMessage = { role: 'assistant', content: response.response };
      setMessages([...updatedMessages, botMessage]);
      
    } catch (err) {
      console.error('Error getting bot reply:', err);
      setError('Failed to get response. Please try again.');
      
      // Add error message to conversation
      const errorMessage = { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try asking your question again.' 
      };
      setMessages([...updatedMessages, errorMessage]);
    } finally {
      setIsLoading(false);
      // Refocus input for next question
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  /**
   * Handle input change
   */
  const handleInputChange = (e) => {
    setCurrentInput(e.target.value);
  };

  /**
   * Handle Enter key press for submission
   */
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  /**
   * Clear conversation history
   */
  const clearHistory = () => {
    setMessages([]);
    setError(null);
    inputRef.current?.focus();
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 p-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <Link 
              to="/" 
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors flex items-center justify-center"
              title="Back to Homepage"
            >
              <ArrowLeft className="h-5 w-5 text-gray-600" />
            </Link>
            <h1 className="text-2xl font-bold text-gray-800">Chat Assistant</h1>
          </div>
          {messages.length > 0 && (
            <button
              onClick={clearHistory}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              disabled={isLoading}
            >
              Clear History
            </button>
          )}
        </div>
      </div>

      {/* Chat Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <div className="text-lg mb-2">👋 Welcome to Chat Assistant!</div>
            <p>Ask me anything and I'll help you based on the uploaded documents and our conversation history.</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl break-words ${
                  message.role === 'user'
                    ? 'bg-blue-500 text-white rounded-br-sm'
                    : 'bg-white border border-gray-200 text-gray-800 rounded-bl-sm shadow-sm'
                }`}
              >
                {/* Message role indicator for screen readers */}
                <span className="sr-only">
                  {message.role === 'user' ? 'You said:' : 'Assistant replied:'}
                </span>
                
                {/* Message content */}
                <div className="whitespace-pre-wrap">{message.content}</div>
                
                {/* Message metadata */}
                <div className={`text-xs mt-2 ${
                  message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                }`}>
                  {message.role === 'user' ? 'You' : 'Assistant'}
                </div>
              </div>
            </div>
          ))
        )}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm shadow-sm px-4 py-3 max-w-xs">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="text-sm text-gray-500">Assistant is typing...</span>
              </div>
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            <div className="flex items-center">
              <span className="text-red-500 mr-2">⚠️</span>
              {error}
            </div>
          </div>
        )}

        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="bg-white border-t border-gray-200 p-4">
        <form onSubmit={handleSubmit} className="flex space-x-3">
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={currentInput}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={1}
              disabled={isLoading}
              style={{ minHeight: '50px', maxHeight: '120px' }}
              onInput={(e) => {
                // Auto-resize textarea
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
              }}
            />
          </div>
          <button
            type="submit"
            disabled={!currentInput.trim() || isLoading}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              'Send'
            )}
          </button>
        </form>
        
        {/* Input hint */}
        <div className="text-xs text-gray-500 mt-2 px-1">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  );
};

export default ChatAsk;