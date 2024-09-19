import { useEffect, useRef, useState } from 'react';

export const useWebSocket = (url: string) => {
    const [response, setResponse] = useState<string>('');
    const [isOpen, setIsOpen] = useState<boolean>(false);
    const socketRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        const socket = new WebSocket(url);
        socketRef.current = socket;

        socket.onopen = () => {
            console.log('WebSocket connection opened');
            setIsOpen(true);
        };

        socket.onmessage = (event) => {
            console.log('Message from server: ', event.data);
            setResponse(event.data);
        };

        socket.onclose = () => {
            console.log('WebSocket connection closed');
            setIsOpen(false);
        };

        socket.onerror = (error) => {
            console.log('WebSocket error: ', error);
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
        } else {
            console.log('WebSocket connection is not open');
        }
    };

    return { response, isOpen, sendMessage };
};
