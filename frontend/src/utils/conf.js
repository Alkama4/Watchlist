const localIP = window.location.hostname; // will be the IP the browser used
export const API_BASE_URL = import.meta.env.DEV 
    ? `http://${localIP}:8000` 
    : '/api';

export const preferredLocale = {
    iso_3166_1: "FI",
    tag: "fi-FI"
}
