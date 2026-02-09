/**
 * EVEZ666 Threshold Navigation Mesh - Offline Store
 * IndexedDB/PouchDB wrapper for offline-first data persistence
 */

'use strict';

// Database configuration
const DB_NAME = 'evez666-offline';
const DB_VERSION = 1;

// Store names
const STORES = {
  NAV_LOG: 'nav_logs',
  RESOURCE_CACHE: 'resource_cache',
  GATE_STATE: 'gate_state',
};

/**
 * Navigation log entry
 */
export interface NavLogEntry {
  id?: string;
  path_used: string;
  threshold: 'wealth' | 'info' | 'myth';
  latency_ms: number;
  breach_attempts: number;
  route_status: 'primary' | 'failover' | 'local';
  timestamp: number;
}

/**
 * Resource cache entry
 */
export interface ResourceCacheEntry {
  key: string;
  threshold: 'wealth' | 'info' | 'myth';
  payload: any;
  cached_at: number;
  expires_at: number;
  sync_status: 'pending' | 'synced' | 'conflict';
}

/**
 * Gate state entry
 */
export interface GateStateEntry {
  cell_id: string;
  jwt_hash?: string;
  anomaly_count: number;
  lockdown: boolean;
  last_validated: number;
  updated_at: number;
}

/**
 * Offline store for navigation mesh data
 */
export class OfflineStore {
  private db: IDBDatabase | null = null;

  constructor() {}

  /**
   * Initialize the IndexedDB database
   */
  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Nav logs store
        if (!db.objectStoreNames.contains(STORES.NAV_LOG)) {
          const navStore = db.createObjectStore(STORES.NAV_LOG, {
            keyPath: 'id',
            autoIncrement: true,
          });
          navStore.createIndex('threshold', 'threshold', { unique: false });
          navStore.createIndex('timestamp', 'timestamp', { unique: false });
        }

        // Resource cache store
        if (!db.objectStoreNames.contains(STORES.RESOURCE_CACHE)) {
          const cacheStore = db.createObjectStore(STORES.RESOURCE_CACHE, {
            keyPath: 'key',
          });
          cacheStore.createIndex('threshold', 'threshold', { unique: false });
          cacheStore.createIndex('sync_status', 'sync_status', { unique: false });
        }

        // Gate state store
        if (!db.objectStoreNames.contains(STORES.GATE_STATE)) {
          const gateStore = db.createObjectStore(STORES.GATE_STATE, {
            keyPath: 'cell_id',
          });
          gateStore.createIndex('lockdown', 'lockdown', { unique: false });
        }
      };
    });
  }

  /**
   * Add navigation log entry
   */
  async addNavLog(entry: NavLogEntry): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const tx = this.db!.transaction(STORES.NAV_LOG, 'readwrite');
      const store = tx.objectStore(STORES.NAV_LOG);
      const request = store.add({
        ...entry,
        timestamp: entry.timestamp || Date.now(),
      });

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get navigation logs by threshold
   */
  async getNavLogs(threshold?: string, limit: number = 100): Promise<NavLogEntry[]> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const tx = this.db!.transaction(STORES.NAV_LOG, 'readonly');
      const store = tx.objectStore(STORES.NAV_LOG);
      
      let request: IDBRequest;
      if (threshold) {
        const index = store.index('threshold');
        request = index.getAll(threshold, limit);
      } else {
        request = store.getAll(null, limit);
      }

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Cache resource
   */
  async cacheResource(entry: ResourceCacheEntry): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const tx = this.db!.transaction(STORES.RESOURCE_CACHE, 'readwrite');
      const store = tx.objectStore(STORES.RESOURCE_CACHE);
      const request = store.put({
        ...entry,
        cached_at: entry.cached_at || Date.now(),
      });

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get cached resource
   */
  async getCachedResource(key: string): Promise<ResourceCacheEntry | null> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const tx = this.db!.transaction(STORES.RESOURCE_CACHE, 'readonly');
      const store = tx.objectStore(STORES.RESOURCE_CACHE);
      const request = store.get(key);

      request.onsuccess = () => {
        const result = request.result;
        // Check expiration
        if (result && result.expires_at && Date.now() > result.expires_at) {
          resolve(null);
        } else {
          resolve(result || null);
        }
      };
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get pending sync resources
   */
  async getPendingSyncResources(): Promise<ResourceCacheEntry[]> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const tx = this.db!.transaction(STORES.RESOURCE_CACHE, 'readonly');
      const store = tx.objectStore(STORES.RESOURCE_CACHE);
      const index = store.index('sync_status');
      const request = index.getAll('pending');

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Update gate state
   */
  async updateGateState(state: GateStateEntry): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const tx = this.db!.transaction(STORES.GATE_STATE, 'readwrite');
      const store = tx.objectStore(STORES.GATE_STATE);
      const request = store.put({
        ...state,
        updated_at: Date.now(),
      });

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get gate state
   */
  async getGateState(cell_id: string): Promise<GateStateEntry | null> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const tx = this.db!.transaction(STORES.GATE_STATE, 'readonly');
      const store = tx.objectStore(STORES.GATE_STATE);
      const request = store.get(cell_id);

      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get all gate states
   */
  async getAllGateStates(): Promise<GateStateEntry[]> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const tx = this.db!.transaction(STORES.GATE_STATE, 'readonly');
      const store = tx.objectStore(STORES.GATE_STATE);
      const request = store.getAll();

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Sync to remote - stub for future implementation
   */
  async syncToRemote(): Promise<{ synced: number; conflicts: number }> {
    const pending = await this.getPendingSyncResources();
    
    // In a real implementation, this would push to remote server
    // For now, just mark as synced
    for (const resource of pending) {
      resource.sync_status = 'synced';
      await this.cacheResource(resource);
    }

    return { synced: pending.length, conflicts: 0 };
  }

  /**
   * Resolve conflicts - stub for future implementation
   */
  async resolveConflicts(): Promise<number> {
    // In a real implementation, this would handle conflict resolution
    return 0;
  }

  /**
   * Get latency tolerance metric
   * Returns percentage of operations that can survive offline
   */
  async getLatencyTolerance(): Promise<number> {
    const logs = await this.getNavLogs();
    if (logs.length === 0) return 100;

    const offlineCapable = logs.filter(
      (log) => log.route_status === 'local' || log.route_status === 'failover'
    ).length;

    return Math.round((offlineCapable / logs.length) * 100);
  }

  /**
   * Close database connection
   */
  close(): void {
    if (this.db) {
      this.db.close();
      this.db = null;
    }
  }
}

// Singleton instance
let storeInstance: OfflineStore | null = null;

/**
 * Get or create offline store instance
 */
export async function getOfflineStore(): Promise<OfflineStore> {
  if (!storeInstance) {
    storeInstance = new OfflineStore();
    await storeInstance.init();
  }
  return storeInstance;
}
