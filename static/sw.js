
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open('finance-store').then((cache) => cache.addAll([
      '/',
      '/dashboard.py',
      '/manifest.json'
    ])),
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((response) => response || fetch(e.request)),
  );
});
