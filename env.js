// Samadhan 24/7 - Runtime Environment Configuration
// For plain HTML / Live Server (port 5500) and production deployment
window.ENV = window.ENV || {};
window.ENV.VITE_GOOGLE_MAPS_API_KEY = window.ENV.VITE_GOOGLE_MAPS_API_KEY || "";
window.ENV.GOOGLE_MAPS_API_KEY = window.ENV.GOOGLE_MAPS_API_KEY || window.ENV.VITE_GOOGLE_MAPS_API_KEY || "";
