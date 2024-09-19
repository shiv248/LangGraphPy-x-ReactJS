import React, { useState, useEffect, ChangeEvent, KeyboardEvent, useRef } from 'react';
import './App.css';

const App: React.FC = () => {
  const [messages, setMessages] = useState<{ user: string, msg: string }[]>([]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null); // Ref to track the end of messages

  const handleChange = (event: ChangeEvent<HTMLTextAreaElement>) => {
    setInput(event.target.value);
  };

  const handleSubmit = () => {
    if (input.trim()) {
      const userMessage = { user: 'User', msg: input };
      const botMessage = { user: 'Bot', msg: input };

      // Append both user's and bot's messages to the conversation
      const updatedMessages = [...messages, userMessage, botMessage];
      setMessages(updatedMessages);

      // Clear the input
      setInput('');
    }
  };

  // Auto-scroll to the bottom when messages are updated
  useEffect(() => {
    // Delay the scroll to ensure new content is rendered
    const timer = setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);

    return () => clearTimeout(timer); // Clean up timer
  }, [messages]);

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault(); // Prevent newline insertion
      handleSubmit(); // Submit the form
    }
  };

  return (
      <div className="App">
        <div className="chat-container">
          <div className="messages">
            {messages.map((msg, index) => (
                <div key={index} className={msg.user === 'User' ? 'message user' : 'message bot'}>
                  <strong>{msg.user}: </strong>
                  <br />
                  {msg.msg}
                </div>
            ))}
            <div ref={messagesEndRef} /> {/* Empty div to track the end of the messages */}
          </div>
          <form className="chat-form" onSubmit={(e) => e.preventDefault()}>
          <textarea
              value={input}
              onChange={handleChange}
              onKeyDown={handleKeyDown}
              placeholder="Type or paste your message..."
              rows={4} // Allows multiple lines
          />
            <button type="button" onClick={handleSubmit}>Send</button>
          </form>
        </div>
      </div>
  );
}

export default App;
