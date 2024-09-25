import React, { useState, useEffect, ChangeEvent, KeyboardEvent, useRef } from 'react';
import { useWebSocket } from './services/useWebSocket'; // Custom hook to manage WebSocket connection
import EE from './components/easter_egg/ee'; // Easter egg component
import './App.css';

const App: React.FC = () => {
    const [messages, setMessages] = useState<{ user: string, msg: string }[]>([
        { user: 'Bot', msg: 'Welcome! How can I be of service today?' } // Initial bot message
    ]);
    const [input, setInput] = useState(''); // User input state
    const [showEE, setShowEE] = useState(false); // Toggle for Easter egg component

    // WebSocket connection logic (message handling & status tracking)
    const { response, isOpen, sendMessage } = useWebSocket('ws://localhost:8000/ws', setShowEE);
    const messagesEndRef = useRef<HTMLDivElement>(null); // Ref for scrolling to the latest message

    useEffect(() => {
        // Handle WebSocket responses and update messages
        if (response) {
            setMessages((prevMessages) => {
                const lastMessage = prevMessages[prevMessages.length - 1];
                // Update last bot message or add a new one
                if (lastMessage && lastMessage.user === 'Bot') {
                    lastMessage.msg = response;
                    return [...prevMessages];
                } else {
                    return [...prevMessages, { user: 'Bot', msg: response }];
                }
            });
        }
    }, [response]);

    // Updates input field on change
    const handleChange = (event: ChangeEvent<HTMLTextAreaElement>) => {
        setInput(event.target.value);
    };

    // Handles sending of messages from the user
    const handleSubmit = () => {
        if (input.trim()) {
            const userMessage = { user: 'User', msg: input };
            setMessages((prevMessages) => [...prevMessages, userMessage]); // Add user message to list
            setInput('');

            if (isOpen) {
                sendMessage(input); // Send message via WebSocket if open
            }
        }
    };

    // Scrolls to the latest token in the chat whenever a new message is added
    useEffect(() => {
        const timer = setTimeout(() => {
            messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }); // , 100); // you can add delay for scrolling, giving user a moment to read message bots message,
                       // but looks slightly jittery

        return () => clearTimeout(timer);  // Cleanup the timeout
    }, [messages]);

    // Handles "Enter" key submission without needing to click the send button
    const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // Prevent default newline
            handleSubmit();
        }
    };

    return (
        <div className="App">
            <div className="chat-header">
                {/* Connection status indicator and title */}
                <div className={`connection-status ${isOpen ? 'online' : 'offline'}`}></div>
                <b>LangGraph-Python 🤝 ReactJS</b>
            </div>
            <div className="chat-container">
                {/* Display chat messages */}
                <div className="messages">
                    {messages.map((msg, index) => (
                        <div key={index} className={msg.user === 'User' ? 'message user' : 'message bot'}>
                            <strong>{msg.user}: </strong>
                            <br />
                            {msg.msg}
                        </div>
                    ))}
                    <div ref={messagesEndRef} /> {/* Reference to scroll to the latest message */}
                </div>
                {/* Input form for typing and sending messages */}
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
                {showEE && <EE />} {/* Easter egg component */}
            </div>
        </div>
    );
}

export default App;
