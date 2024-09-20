import { useEffect, useRef, useState } from 'react';
import { generate } from "random-words";

export const useWebSocket = (url: string) => {
    const [response, setResponse] = useState<string>('');
    const [isOpen, setIsOpen] = useState<boolean>(false);
    const [isBotResponseComplete, setIsBotResponseComplete] = useState<boolean>(false);
    const socketRef = useRef<WebSocket | null>(null);
    const wordUUIDRef = useRef<string>((generate({ exactly: 4 }) as string[]).join('-'));

    useEffect(() => {
        const socket = new WebSocket(url);
        socketRef.current = socket;

        socket.onopen = () => {
            console.log('WebSocket connection opened');
            setIsOpen(true);
            // Send the UUID with init flag to the server
            socket.send(JSON.stringify({ uuid: wordUUIDRef.current, init: true }));
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('Received from server:', data);

                if (data.on_chat_model_stream) {
                    setResponse((prevResponse) => prevResponse + data.on_chat_model_stream);
                }

                if (data.on_chat_model_end) {
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
            const payload = {
                uuid: wordUUIDRef.current,
                message,
                init: false
            };
            socketRef.current.send(JSON.stringify(payload));
            setIsBotResponseComplete(false);
            setResponse('');
        } else {
            console.log('WebSocket connection is not open');
        }
    };

    return { response, isOpen, isBotResponseComplete, sendMessage };
};
