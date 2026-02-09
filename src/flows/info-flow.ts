/**
 * EVEZ666 Threshold Navigation Mesh - Info Flow
 * Archive cell with offline scan and PouchDB-backed document store
 */

'use strict';

export interface ArchiveDocument {
  id: string;
  title: string;
  content: string;
  tags: string[];
  source: string;
  timestamp: number;
  metadata?: Record<string, any>;
}

export interface RSSFeedEntry {
  url: string;
  title: string;
  content: string;
  published: number;
  cached: boolean;
}

export interface SearchResult {
  document: ArchiveDocument;
  score: number;
  matches: string[];
}

/**
 * Info flow manager for archive operations
 */
export class InfoFlow {
  private documents: Map<string, ArchiveDocument> = new Map();
  private rssCache: Map<string, RSSFeedEntry[]> = new Map();
  private syncStatus: 'idle' | 'syncing' | 'error' = 'idle';
  private lastSyncTime: number = 0;

  constructor() {}

  /**
   * Add document to archive
   */
  async addDocument(doc: ArchiveDocument): Promise<void> {
    this.documents.set(doc.id, {
      ...doc,
      timestamp: doc.timestamp || Date.now(),
    });
  }

  /**
   * Get document by ID
   */
  async getDocument(id: string): Promise<ArchiveDocument | null> {
    return this.documents.get(id) || null;
  }

  /**
   * Search archive (offline-capable)
   */
  async searchArchive(query: string, limit: number = 10): Promise<SearchResult[]> {
    const results: SearchResult[] = [];
    const queryLower = query.toLowerCase();

    for (const doc of this.documents.values()) {
      const matches: string[] = [];
      let score = 0;

      // Search in title
      if (doc.title.toLowerCase().includes(queryLower)) {
        matches.push(`title: ${doc.title}`);
        score += 10;
      }

      // Search in content
      const contentMatches = this.findMatches(doc.content, queryLower);
      if (contentMatches.length > 0) {
        matches.push(...contentMatches);
        score += contentMatches.length * 5;
      }

      // Search in tags
      for (const tag of doc.tags) {
        if (tag.toLowerCase().includes(queryLower)) {
          matches.push(`tag: ${tag}`);
          score += 3;
        }
      }

      if (score > 0) {
        results.push({ document: doc, score, matches });
      }
    }

    // Sort by score and limit
    results.sort((a, b) => b.score - a.score);
    return results.slice(0, limit);
  }

  /**
   * Find matches in text
   */
  private findMatches(text: string, query: string): string[] {
    const matches: string[] = [];
    const textLower = text.toLowerCase();
    let index = textLower.indexOf(query);

    while (index !== -1 && matches.length < 3) {
      // Extract context around match
      const start = Math.max(0, index - 30);
      const end = Math.min(text.length, index + query.length + 30);
      const context = text.substring(start, end);
      matches.push(`...${context}...`);
      
      index = textLower.indexOf(query, index + 1);
    }

    return matches;
  }

  /**
   * Fetch and cache RSS feed
   */
  async fetchRSSFeed(url: string): Promise<RSSFeedEntry[]> {
    // Check cache first
    const cached = this.rssCache.get(url);
    if (cached) {
      return cached;
    }

    try {
      // In production, fetch from actual RSS feed
      // For now, simulate with mock data
      const entries = await this.simulateFetchRSS(url);
      
      // Cache the entries
      this.rssCache.set(url, entries);
      
      return entries;
    } catch (error) {
      // If fetch fails, return empty array (offline-capable)
      console.warn(`[InfoFlow] Failed to fetch RSS feed: ${url}`);
      return [];
    }
  }

  /**
   * Simulate RSS fetch
   */
  private async simulateFetchRSS(url: string): Promise<RSSFeedEntry[]> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          {
            url: `${url}/entry1`,
            title: 'Sample Entry 1',
            content: 'This is sample content from RSS feed',
            published: Date.now() - 3600000,
            cached: true,
          },
          {
            url: `${url}/entry2`,
            title: 'Sample Entry 2',
            content: 'Another sample entry',
            published: Date.now() - 7200000,
            cached: true,
          },
        ]);
      }, 100);
    });
  }

  /**
   * Get cached RSS feeds
   */
  getCachedFeeds(): string[] {
    return Array.from(this.rssCache.keys());
  }

  /**
   * Opportunistic sync with remote
   */
  async syncWithRemote(): Promise<{
    pushed: number;
    pulled: number;
    conflicts: number;
  }> {
    if (this.syncStatus === 'syncing') {
      throw new Error('Sync already in progress');
    }

    this.syncStatus = 'syncing';

    try {
      // In production, sync with remote PouchDB/CouchDB
      // For now, simulate sync
      await new Promise((resolve) => setTimeout(resolve, 500));

      this.lastSyncTime = Date.now();
      this.syncStatus = 'idle';

      return {
        pushed: 0,
        pulled: 0,
        conflicts: 0,
      };
    } catch (error) {
      this.syncStatus = 'error';
      throw error;
    }
  }

  /**
   * Get sync status
   */
  getSyncStatus(): {
    status: string;
    lastSync: number;
    documentCount: number;
  } {
    return {
      status: this.syncStatus,
      lastSync: this.lastSyncTime,
      documentCount: this.documents.size,
    };
  }

  /**
   * Batch import documents
   */
  async batchImport(docs: ArchiveDocument[]): Promise<{
    imported: number;
    failed: number;
  }> {
    let imported = 0;
    let failed = 0;

    for (const doc of docs) {
      try {
        await this.addDocument(doc);
        imported++;
      } catch (error) {
        failed++;
      }
    }

    return { imported, failed };
  }

  /**
   * Get archive statistics
   */
  getStatistics(): {
    totalDocuments: number;
    totalTags: number;
    sources: string[];
    oldestDocument: number;
    newestDocument: number;
  } {
    const tags = new Set<string>();
    const sources = new Set<string>();
    let oldest = Date.now();
    let newest = 0;

    for (const doc of this.documents.values()) {
      doc.tags.forEach((tag) => tags.add(tag));
      sources.add(doc.source);
      oldest = Math.min(oldest, doc.timestamp);
      newest = Math.max(newest, doc.timestamp);
    }

    return {
      totalDocuments: this.documents.size,
      totalTags: tags.size,
      sources: Array.from(sources),
      oldestDocument: oldest,
      newestDocument: newest,
    };
  }

  /**
   * Clear cache (for testing)
   */
  clearCache(): void {
    this.rssCache.clear();
  }

  /**
   * Clear documents (for testing)
   */
  clearDocuments(): void {
    this.documents.clear();
  }
}

// Singleton instance
let infoFlowInstance: InfoFlow | null = null;

/**
 * Get or create info flow instance
 */
export function getInfoFlow(): InfoFlow {
  if (!infoFlowInstance) {
    infoFlowInstance = new InfoFlow();
  }
  return infoFlowInstance;
}
