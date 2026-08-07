// Minimal service worker used by the extension background in MV3
console.log('TruChat background worker (source) loaded');

self.addEventListener('install', (ev) => {
  console.log('background worker install');
  self.skipWaiting();
});

self.addEventListener('activate', (ev) => {
  console.log('background worker activate');
});

// Example listener: respond to messages from extension pages/popup
self.addEventListener('message', (ev) => {
  console.log('background received message', ev.data);
});
