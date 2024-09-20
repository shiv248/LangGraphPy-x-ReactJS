import { useEffect, useRef, useState, useCallback } from 'react';
import { generate } from "random-words";

export const useWebSocket = (url: string, setEE: (value: boolean) => void) => {
    const [response, setResponse] = useState<string>('');
    const [isOpen, setIsOpen] = useState<boolean>(false);
    const [isBotResponseComplete, setIsBotResponseComplete] = useState<boolean>(false);
    const socketRef = useRef<WebSocket | null>(null);
    const wordUUIDRef = useRef<string>((generate({ exactly: 4 }) as string[]).join('-'));
    const messageQueueRef = useRef<string[]>([]);
    const retryCountRef = useRef<number>(0);
    const maxRetries = 5;

    const connectSocket = useCallback(() => {
        const socket = new WebSocket(url);
        socketRef.current = socket;

        socket.onopen = () => {
            console.log('WebSocket connection opened for', wordUUIDRef.current);
            setIsOpen(true);
            retryCountRef.current = 0;
            socket.send(JSON.stringify({ uuid: wordUUIDRef.current, init: true }));

            // Send any queued messages
            while (messageQueueRef.current.length > 0) {
                const message = messageQueueRef.current.shift();
                if (message) {
                    sendMessage(message);
                }
            }
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

                if(data.on_easter_egg){
                    setEE(true);
                }
            } catch (error) {
                console.log('Error parsing WebSocket message:', error);
            }
        };

        socket.onclose = () => {
            console.log('WebSocket connection closed');
            setIsOpen(false);

            if (retryCountRef.current < maxRetries) {
                retryCountRef.current += 1;
                console.log(`Attempting to reconnect (${retryCountRef.current}/${maxRetries}) in 3 seconds...`);
                setTimeout(connectSocket, 3000);
            } else {
                console.log('Max reconnection attempts reached. Stopping reconnection.');
            }
        };

        socket.onerror = (error) => {
            console.log('WebSocket error:', error);
        };
    }, [url, setEE]);

    useEffect(() => {
        connectSocket();

        return () => {
            if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
                socketRef.current.close();
            }
        };
    }, [connectSocket]);

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
            console.log('WebSocket connection is not open, queuing message:', message);
            messageQueueRef.current.push(message);
        }
    };

    return { response, isOpen, isBotResponseComplete, sendMessage };
};