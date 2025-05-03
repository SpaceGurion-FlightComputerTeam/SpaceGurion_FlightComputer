const socket = new WebSocket('ws://localhost:8765');
const listeners = [];

socket.onopen = () => {
    console.log("[WebSocket] Connected");
    document.getElementById("connectBtn").disabled = false;
};

socket.onerror = (err) => {
    console.error("[WebSocket] Error:", err);
};

socket.onclose = () => {
    console.log("[WebSocket] Closed");
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    listeners.forEach(fn => fn(data));
};

export function send(data) {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(data));
    } else {
        console.warn("[WebSocket] Not open");
    }
}

export function addMessageListener(callback) {
    listeners.push(callback);
}

export { socket };