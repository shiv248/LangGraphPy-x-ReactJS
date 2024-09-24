import React, { useState, useEffect, ChangeEvent, KeyboardEvent, useRef } from 'react';
import { useWebSocket } from './services/useWebSocket';
import EE from './components/easter_egg/ee';
import './App.css';

const App: React.FC = () => {
    // Initial bot message added to the state
    const [messages, setMessages] = useState<{ user: string, msg: string }[]>([
        { user: 'Bot', msg: 'Welcome! How can I be of service today?' }
    ]);
    const [input, setInput] = useState('');
    const [showEE, setShowEE] = useState(false);
    const { response, isOpen, sendMessage } = useWebSocket('ws://localhost:8000/ws', setShowEE);
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
            setInput('');

            if (isOpen) {
                sendMessage(input);
            }
        }
    };

    useEffect(() => {
        const timer = setTimeout(() => {
            messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }); // , 100); // you can add delay for scrolling, giving user a moment to read message bots message,
                       // but looks slightly jittery

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
                {showEE && <EE />}
            </div>
        </div>
    );
}

export default App;
