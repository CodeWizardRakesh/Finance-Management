import React, { useEffect, useRef } from 'react';
import { Message } from '../types';
import MessageBubble from './MessageBubble';
import LoadingSpinner from './LoadingSpinner';
import { TrendingUp } from 'lucide-react';

interface ConversationViewProps {
  messages: Message[];
  isLoading: boolean;
}

const ConversationView: React.FC<ConversationViewProps> = ({ messages, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="flex-1 bg-black overflow-hidden flex flex-col">
      <div className="bg-gray-900 border-b border-gray-800 p-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center">
            <TrendingUp size={20} className="text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">AI Financial Advisor</h1>
            <p className="text-sm text-gray-400">Your personal finance companion</p>
          </div>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 scroll-smooth">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <div className="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center mb-4">
              <TrendingUp size={32} className="text-white" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Welcome to Your Financial Advisor</h2>
            <p className="text-gray-400 max-w-md mb-6">
              I'm here to help you with budgeting, investments, savings strategies, and all your financial questions. 
              Start by asking me anything about your finances!
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-lg">
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-3 text-left">
                <p className="text-sm text-gray-300 font-medium">💰 "How should I create a monthly budget?"</p>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-3 text-left">
                <p className="text-sm text-gray-300 font-medium">📈 "What are the best investment strategies?"</p>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-3 text-left">
                <p className="text-sm text-gray-300 font-medium">🏠 "Should I buy a house or keep renting?"</p>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-3 text-left">
                <p className="text-sm text-gray-300 font-medium">💳 "How can I pay off my credit card debt?"</p>
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {isLoading && <LoadingSpinner />}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ConversationView;