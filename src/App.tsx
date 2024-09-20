import React, { useState, useEffect, ChangeEvent, KeyboardEvent, useRef } from 'react';
import { useWebSocket } from './services/useWebSocket';
import './App.css';

const App: React.FC = () => {
    const [messages, setMessages] = useState<{ user: string, msg: string }[]>([]);
    const [input, setInput] = useState('');
    const { response, isOpen, sendMessage } = useWebSocket('ws://localhost:8000/ws');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (response) {
            setMessages((prevMessages) => {
                const lastMessage = prevMessages[prevMessages.length - 1];
                if (lastMessage && lastMessage.user === 'Bot') {
                    lastMessage.msg = response;
                    return [...prevMessages];
                } else {
                    return [...prevMessages, { user: 'Bot', msg: response }];
                }
            });
        }
    }, [response]);

    const handleChange = (event: ChangeEvent<HTMLTextAreaElement>) => {
        setInput(event.target.value);
    };

    const handleSubmit = () => {
        if (input.trim()) {
            const userMessage = { user: 'User', msg: input };

            setMessages((prevMessages) => [...prevMessages, userMessage]);

            // Clear the input
            setInput('');

            if (isOpen) {
                sendMessage(input);
            }
        }
    };

    // Scroll to the bottom when new messages are added
    useEffect(() => {
        const timer = setTimeout(() => {
            messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }, 100);

        return () => clearTimeout(timer);
    }, [messages]);

    const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSubmit();
        }
    };

    return (
        <div className="App">
            <div className="chat-header">
                <div className={`connection-status ${isOpen ? 'online' : 'offline'}`}></div>
                <b>LangGraph-Python 🤝 ReactJS</b>
            </div>
            <div className="chat-container">
                <div className="messages">
                    {messages.map((msg, index) => (
                        <div key={index} className={msg.user === 'User' ? 'message user' : 'message bot'}>
                            <strong>{msg.user}: </strong>
                            <br />
                            {msg.msg}
                        </div>
                    ))}
                    <div ref={messagesEndRef} />
                </div>
                <form className="chat-form" onSubmit={(e) => e.preventDefault()}>
                    <textarea
                        value={input}
                        onChange={handleChange}
                        onKeyDown={handleKeyDown}
                        placeholder="Type or paste your message..."
                        rows={4}
                    />
                    <button type="button" onClick={handleSubmit}>Send</button>
                </form>
            </div>
        </div>
    );
}

export default App;
