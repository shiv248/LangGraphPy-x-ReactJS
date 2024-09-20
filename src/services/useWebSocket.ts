import { useEffect, useRef, useState } from 'react';

export const useWebSocket = (url: string) => {
    const [response, setResponse] = useState<string>('');
    const [isOpen, setIsOpen] = useState<boolean>(false);
    const [isBotResponseComplete, setIsBotResponseComplete] = useState<boolean>(false);
    const socketRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        const socket = new WebSocket(url);
        socketRef.current = socket;

        socket.onopen = () => {
            console.log('WebSocket connection opened');
            setIsOpen(true);
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('Received from server:', data);

                if (data.on_chat_model_stream) {
                    // Append the token to the response
                    setResponse((prevResponse) => prevResponse + data.on_chat_model_stream);
                }

                if (data.on_chat_model_end) {
                    // Bot response is complete
                    setIsBotResponseComplete(true);
                }
            } catch (error) {
                console.log('Error parsing WebSocket message:', error);
            }
        };

        socket.onclose = () => {
            console.log('WebSocket connection closed');
            setIsOpen(false);
        };

        socket.onerror = (error) => {
            console.log('WebSocket error:', error);
        };

        return () => {
            if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
                socketRef.current.close();
            }
        };
    }, [url]);

    const sendMessage = (message: string) => {
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
            socketRef.current.send(message);
            setIsBotResponseComplete(false); // Reset the response state for the next message
            setResponse(''); // Clear the current response when a new message is sent
        } else {
            console.log('WebSocket connection is not open');
        }
    };

    return { response, isOpen, isBotResponseComplete, sendMessage };
};
