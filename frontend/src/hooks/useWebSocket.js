import { useState, useEffect, useCallback, useRef } from 'react';

const WS_URL = 'ws://localhost:8000/ws/leads';

export const useWebSocket = () => {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef(null);

  const connect = useCallback(() => {
    ws.current = new WebSocket(WS_URL);

    ws.current.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => [...prev, data]);
    };

    ws.current.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected. Reconnecting...');
      // Try to reconnect
      setTimeout(() => {
        connect();
      }, 5000);
    };
    
    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      ws.current.close();
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connect]);

  // Method to clear the messages after they are processed by the UI
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return { messages, isConnected, clearMessages };
};
