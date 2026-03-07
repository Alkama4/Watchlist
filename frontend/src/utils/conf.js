const localIP = window.location.hostname; // will be the IP the browser used
export const API_BASE_URL = import.meta.env.DEV 
    ? `http://${localIP}:8000` 
    : '/api';
