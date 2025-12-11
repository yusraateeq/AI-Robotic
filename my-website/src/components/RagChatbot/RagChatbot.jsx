import React, { useState, useRef, useEffect } from 'react';
import './RagChatbot.css';

const RagChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [selectedText, setSelectedText] = useState('');
  const [showTextSelectionHelp, setShowTextSelectionHelp] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Track text selection
  useEffect(() => {
    const handleTextSelection = () => {
      const selection = window.getSelection();
      if (selection.toString().trim() !== '') {
        setSelectedText(selection.toString().trim());
        setShowTextSelectionHelp(true);
        setTimeout(() => setShowTextSelectionHelp(false), 3000);
      }
    };
    document.addEventListener('mouseup', handleTextSelection);
    return () => document.removeEventListener('mouseup', handleTextSelection);
  }, []);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: selectedText ? `Context: ${selectedText}\nQuestion: ${inputValue}` : inputValue,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const endpoint = selectedText ? '/api/chat/query_with_context' : '/api/chat/query';
      const requestBody = selectedText
        ? { query: inputValue, context: selectedText, session_id: sessionId || undefined }
        : { query: inputValue, session_id: sessionId || undefined };

      // Use direct backend URL here
      const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) throw new Error(`API request failed: ${response.status}`);

      const data = await response.json();

      if (data.session_id && !sessionId) setSessionId(data.session_id);

      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.response,
        sources: data.sources || [],
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);
      setSelectedText('');
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        error: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleUseSelectedText = () => {
    setInputValue(`About: "${selectedText}" `);
    setSelectedText('');
    textareaRef.current?.focus();
  };

  return (
    <div className="rag-chatbot-container">
      <button
        className="chatbot-toggle"
        onClick={() => setIsChatOpen(!isChatOpen)}
      >
        {isChatOpen ? '✕' : '🤖 AI Assistant'}
      </button>

      {isChatOpen && (
        <div className="chatbot-panel">
          <div className="chatbot-header">
            <h3>AI Textbook Assistant</h3>
            <p>Ask questions about the textbook content</p>
          </div>

          {selectedText && (
            <div className="text-selection-helper">
              <p><strong>Selected text:</strong> "{selectedText.substring(0, 100)}{selectedText.length > 100 ? '...' : ''}"</p>
              <button onClick={handleUseSelectedText}>Use in question</button>
            </div>
          )}

          <div className="messages-container">
            {messages.length === 0 ? (
              <div className="welcome-message">
                <h4>Hello! I'm your AI textbook assistant.</h4>
                <p>Ask me questions or select text on the page.</p>
              </div>
            ) : (
              messages.map(msg => (
                <div key={msg.id} className={`message ${msg.role} ${msg.error ? 'error' : ''}`}>
                  <div className="message-content">{msg.content}</div>
                  {msg.sources?.length > 0 && (
                    <details>
                      <summary>Sources</summary>
                      <ul>
                        {msg.sources.slice(0,3).map((s,i) => (
                          <li key={i}>{s.content.substring(0,150)}{s.content.length>150?'...':''} (Score: {s.score.toFixed(3)})</li>
                        ))}
                      </ul>
                    </details>
                  )}
                </div>
              ))
            )}
            {isLoading && (
              <div className="message assistant">
                <div className="message-content">
                  <div className="typing-indicator"><span></span><span></span><span></span></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="input-container">
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={selectedText ? "Ask about selected text..." : "Ask about textbook content..."}
              rows={3}
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </div>
      )}

      {showTextSelectionHelp && selectedText && (
        <div className="text-selection-tooltip">
          Selected text: "{selectedText.substring(0,50)}{selectedText.length>50?'...':''}"
        </div>
      )}
    </div>
  );
};

export default RagChatbot;
