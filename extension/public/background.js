// Background service worker copied via Vite public directory
console.log('TruChat background worker (public) loaded');

self.addEventListener('install', (ev) => {
  console.log('background worker install');
  self.skipWaiting();
});

self.addEventListener('activate', (ev) => {
  console.log('background worker activate');
});

self.addEventListener('message', (ev) => {
  console.log('background received message', ev.data);
});
