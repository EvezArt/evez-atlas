/**
 * EVEZ666 Threshold Navigation Mesh - Service Worker
 * Workbox-based ServiceWorker for offline-first operation
 */

// Cache version
const CACHE_VERSION = 'evez666-v1';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`;
const API_CACHE = `${CACHE_VERSION}-api`;

// Assets to cache immediately
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] Installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      console.log('[ServiceWorker] Caching static assets');
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn('[ServiceWorker] Failed to cache some assets:', err);
      });
    })
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name.startsWith('evez666-') && name !== STATIC_CACHE && name !== DYNAMIC_CACHE && name !== API_CACHE)
          .map((name) => {
            console.log('[ServiceWorker] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - stale-while-revalidate strategy
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    // Queue POST requests for offline replay
    if (request.method === 'POST') {
      event.respondWith(handlePostRequest(request));
    }
    return;
  }

  // API requests - stale-while-revalidate
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(staleWhileRevalidate(request, API_CACHE));
    return;
  }

  // Static assets - cache first
  if (STATIC_ASSETS.some((asset) => url.pathname === asset)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
    return;
  }

  // Dynamic content - network first
  event.respondWith(networkFirst(request, DYNAMIC_CACHE));
});

// Cache first strategy
async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);
  if (cached) {
    return cached;
  }
  try {
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.error('[ServiceWorker] Fetch failed:', error);
    return new Response('Offline', { status: 503 });
  }
}

// Network first strategy
async function networkFirst(request, cacheName) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    const cache = await caches.open(cacheName);
    const cached = await cache.match(request);
    if (cached) {
      return cached;
    }
    return new Response('Offline', { status: 503 });
  }
}

// Stale-while-revalidate strategy
async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);

  const fetchPromise = fetch(request).then((response) => {
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  }).catch(() => null);

  return cached || fetchPromise || new Response('Offline', { status: 503 });
}

// Handle POST requests - queue for replay
async function handlePostRequest(request) {
  try {
    const response = await fetch(request);
    return response;
  } catch (error) {
    // Queue for replay when back online
    const body = await request.clone().text();
    await queuePostRequest(request.url, body);
    return new Response(JSON.stringify({ queued: true, offline: true }), {
      status: 202,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

// Queue POST request for background sync
async function queuePostRequest(url, body) {
  const db = await openDB();
  const tx = db.transaction('post_queue', 'readwrite');
  await tx.objectStore('post_queue').add({
    url,
    body,
    timestamp: Date.now(),
  });
}

// Open IndexedDB for queue storage
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('evez666-sw', 1);
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('post_queue')) {
        db.createObjectStore('post_queue', { keyPath: 'id', autoIncrement: true });
      }
    };
  });
}

// Background sync - replay queued requests
self.addEventListener('sync', (event) => {
  if (event.tag === 'replay-posts') {
    event.waitUntil(replayQueuedPosts());
  }
});

async function replayQueuedPosts() {
  const db = await openDB();
  const tx = db.transaction('post_queue', 'readonly');
  const queue = await tx.objectStore('post_queue').getAll();

  for (const item of queue) {
    try {
      await fetch(item.url, {
        method: 'POST',
        body: item.body,
        headers: { 'Content-Type': 'application/json' },
      });
      // Remove from queue on success
      const delTx = db.transaction('post_queue', 'readwrite');
      await delTx.objectStore('post_queue').delete(item.id);
    } catch (error) {
      console.warn('[ServiceWorker] Failed to replay:', item.url);
    }
  }
}
