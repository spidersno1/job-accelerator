'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Zap, Clock, AlertCircle, Activity, BarChart3 } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  source?: string;
  confidence?: number;
  suggestions?: string[];
  metadata?: {
    model?: string;
    response_time?: number;
    intent?: string;
    topic?: string;
  };
}

interface UsageStats {
  services: {
    ollama: {
      daily: { used: number; limit: number; remaining: number; percentage: number };
    };
    groq: {
      daily: { used: number; limit: number; remaining: number; percentage: number };
    };
    rule_based: {
      daily: { used: number; limit: number; remaining: number; percentage: number };
    };
  };
  model_availability: {
    ollama: boolean;
    groq: boolean;
    rule_based: boolean;
  };
  total_requests_today: number;
}

export default function FreeAIChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null);
  const [showStats, setShowStats] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // 初始化欢迎消息
    setMessages([{
      id: 'welcome',
      role: 'assistant',
      content: '你好！我是小智，你的免费AI学习助手。我可以帮你分析技能、规划学习路径、解答编程问题。有什么想了解的吗？\n\n💡 提示：我会智能选择最佳的免费AI模型为你服务！',
      timestamp: new Date(),
      source: 'system',
      suggestions: ['技能分析', '学习规划', '求职指导', '编程学习']
    }]);
    
    // 获取使用统计
    fetchUsageStats();
    
    // 定期更新统计（每30秒）
    const interval = setInterval(fetchUsageStats, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchUsageStats = async () => {
    try {
      const response = await fetch('/api/agent/usage-stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      if (data.success) {
        setUsageStats(data.data);
      }
    } catch (error) {
      console.error('获取使用统计失败:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/api/agent/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          message: userMessage.content
        })
      });

      const data = await response.json();

      if (data.success) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.data.response,
          timestamp: new Date(),
          source: data.data.source,
          confidence: data.data.metadata?.confidence,
          suggestions: data.data.suggestions,
          metadata: data.data.metadata
        };

        setMessages(prev => [...prev, assistantMessage]);
        
        // 更新使用统计
        await fetchUsageStats();
      } else {
        throw new Error(data.message || '响应失败');
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '抱歉，我现在有点忙，请稍后再试。你也可以查看我们的帮助文档获取答案。',
        timestamp: new Date(),
        source: 'error'
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
  };

  const getSourceIcon = (source?: string) => {
    switch (source) {
      case 'ollama_local':
        return <Zap className="w-4 h-4 text-green-500" />;
      case 'groq_api':
        return <Bot className="w-4 h-4 text-blue-500" />;
      case 'rule_based':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'system':
        return <Activity className="w-4 h-4 text-purple-500" />;
      default:
        return <Bot className="w-4 h-4 text-gray-500" />;
    }
  };

  const getSourceLabel = (source?: string) => {
    switch (source) {
      case 'ollama_local':
        return '本地AI';
      case 'groq_api':
        return '云端AI';
      case 'rule_based':
        return '智能规则';
      case 'system':
        return '系统';
      default:
        return '未知';
    }
  };

  const getUsageColor = (used: number, limit: number) => {
    if (limit === -1) return 'text-green-500'; // 无限制
    const percentage = (used / limit) * 100;
    if (percentage >= 90) return 'text-red-500';
    if (percentage >= 70) return 'text-yellow-500';
    return 'text-green-500';
  };

  const formatResponseTime = (time?: number) => {
    if (!time) return '';
    return time < 1 ? `${(time * 1000).toFixed(0)}ms` : `${time.toFixed(1)}s`;
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* 顶部状态栏 */}
      <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="w-6 h-6 text-blue-500" />
            <h3 className="font-semibold text-gray-800">小智 - 免费AI助手</h3>
          </div>
          
          <div className="flex items-center gap-2">
            {/* 模型可用性指示器 */}
            {usageStats?.model_availability && (
              <div className="flex items-center gap-1">
                <div className={`w-2 h-2 rounded-full ${usageStats.model_availability.ollama ? 'bg-green-500' : 'bg-gray-300'}`} title="本地AI"></div>
                <div className={`w-2 h-2 rounded-full ${usageStats.model_availability.groq ? 'bg-blue-500' : 'bg-gray-300'}`} title="云端AI"></div>
                <div className={`w-2 h-2 rounded-full ${usageStats.model_availability.rule_based ? 'bg-yellow-500' : 'bg-gray-300'}`} title="规则引擎"></div>
              </div>
            )}
            
            <button
              onClick={() => setShowStats(!showStats)}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-white rounded-lg transition-colors"
              title="使用统计"
            >
              <BarChart3 className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        {/* 使用统计展开面板 */}
        {showStats && usageStats && (
          <div className="mt-3 p-3 bg-white rounded-lg border">
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Zap className="w-4 h-4 text-green-500" />
                  <span className="font-medium">本地AI</span>
                </div>
                <div className="text-green-600">无限制</div>
              </div>
              
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Bot className="w-4 h-4 text-blue-500" />
                  <span className="font-medium">云端AI</span>
                </div>
                <div className={getUsageColor(
                  usageStats.services.groq.daily.used,
                  usageStats.services.groq.daily.limit
                )}>
                  {usageStats.services.groq.daily.used}/{usageStats.services.groq.daily.limit}
                </div>
              </div>
              
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Clock className="w-4 h-4 text-yellow-500" />
                  <span className="font-medium">智能规则</span>
                </div>
                <div className="text-yellow-600">
                  {usageStats.services.rule_based.daily.used}
                </div>
              </div>
            </div>
            
            <div className="mt-2 pt-2 border-t text-center text-xs text-gray-500">
              今日总请求: {usageStats.total_requests_today}
            </div>
          </div>
        )}
      </div>

      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {/* AI消息的元数据 */}
              {message.role === 'assistant' && (
                <div className="flex items-center gap-2 mb-2 text-xs opacity-70">
                  {getSourceIcon(message.source)}
                  <span>{getSourceLabel(message.source)}</span>
                  {message.metadata?.model && (
                    <span className="px-1 bg-black bg-opacity-10 rounded">
                      {message.metadata.model}
                    </span>
                  )}
                  {message.metadata?.response_time && (
                    <span>{formatResponseTime(message.metadata.response_time)}</span>
                  )}
                  {message.confidence && (
                    <span>置信度: {(message.confidence * 100).toFixed(0)}%</span>
                  )}
                </div>
              )}
              
              {/* 消息内容 */}
              <div className="whitespace-pre-wrap">{message.content}</div>
              
              {/* 建议按钮 */}
              {message.suggestions && message.suggestions.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {message.suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="px-2 py-1 text-xs bg-blue-500 bg-opacity-20 text-blue-700 rounded hover:bg-opacity-30 transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              )}
              
              {/* 时间戳 */}
              <div className="text-xs opacity-70 mt-2">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-3 max-w-[80%]">
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                <span className="text-gray-600">小智正在思考...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* 输入框 */}
      <div className="p-4 border-t bg-gray-50">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入你的问题..."
            className="flex-1 resize-none border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={1}
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        
        {/* 免费版提示 */}
        <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
          <AlertCircle className="w-3 h-3" />
          <span>免费版：智能选择最佳模型，本地AI无限制，云端AI有每日限额</span>
        </div>
      </div>
    </div>
  );
} 