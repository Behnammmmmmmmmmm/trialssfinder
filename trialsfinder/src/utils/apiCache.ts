interface CacheOptions {
  ttl?: number;
  max?: number;
}

interface CacheItem<T> {
  data: T;
  expiry: number;
}

class APICache {
  private cache: Map<string, CacheItem<any>>;
  private pendingRequests: Map<string, Promise<any>>;
  private maxSize: number;
  private defaultTTL: number;

  constructor(options: CacheOptions = {}) {
    this.cache = new Map();
    this.pendingRequests = new Map();
    this.maxSize = options.max || 500;
    this.defaultTTL = options.ttl || 1000 * 60 * 5; // 5 minutes default
  }

  generateKey(url: string, params?: any): string {
    const sortedParams = params ? JSON.stringify(params, Object.keys(params).sort()) : '';
    return `${url}:${sortedParams}`;
  }

  private isExpired(item: CacheItem<any>): boolean {
    return Date.now() > item.expiry;
  }

  private evictOldest(): void {
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      if (firstKey) {
        this.cache.delete(firstKey);
      }
    }
  }

  get<T>(key: string): T | undefined {
    const item = this.cache.get(key);
    if (!item) {
      return undefined;
    }
    
    if (this.isExpired(item)) {
      this.cache.delete(key);
      return undefined;
    }
    
    return item.data;
  }

  set<T>(key: string, data: T, ttl?: number): void {
    this.evictOldest();
    
    const expiry = Date.now() + (ttl || this.defaultTTL);
    this.cache.set(key, { data, expiry });
  }

  async getOrFetch<T>(
    url: string,
    fetcher: () => Promise<T>,
    options: { ttl?: number; params?: any } = {}
  ): Promise<T> {
    const key = this.generateKey(url, options.params);
    
    // Check cache first
    const cached = this.get<T>(key);
    if (cached !== undefined) {
      return cached;
    }

    // Check if request is already pending
    const pending = this.pendingRequests.get(key);
    if (pending) {
      return pending;
    }

    // Make request and cache result
    const request = fetcher()
      .then(data => {
        this.set(key, data, options.ttl);
        this.pendingRequests.delete(key);
        return data;
      })
      .catch(error => {
        this.pendingRequests.delete(key);
        throw error;
      });

    this.pendingRequests.set(key, request);
    return request;
  }

  invalidate(pattern?: string): void {
    if (!pattern) {
      this.cache.clear();
      return;
    }

    // Invalidate keys matching pattern
    for (const key of Array.from(this.cache.keys())) {
      if (key.includes(pattern)) {
        this.cache.delete(key);
      }
    }
  }

  invalidateUser(userId: number): void {
    this.invalidate(`user:${userId}`);
  }

  invalidateTrial(trialId: number): void {
    this.invalidate(`trial:${trialId}`);
    this.invalidate('trials:');
  }
}

export const apiCache = new APICache();

// Axios interceptor for automatic caching
export const setupCacheInterceptor = (axiosInstance: any) => {
  // Check if axiosInstance exists and has interceptors
  if (!axiosInstance || !axiosInstance.interceptors) {
    console.warn('Invalid axios instance provided to setupCacheInterceptor');
    return;
  }

  axiosInstance.interceptors.request.use((config: any) => {
    // Only cache GET requests
    if (config.method === 'get' && config.cache !== false) {
      const cacheKey = apiCache.generateKey(config.url, config.params);
      const cached = apiCache.get(cacheKey);
      
      if (cached) {
        config.adapter = () => Promise.resolve({
          data: cached,
          status: 200,
          statusText: 'OK',
          headers: { 'x-cache': 'HIT' },
          config,
        });
      }
    }
    return config;
  });

  axiosInstance.interceptors.response.use((response: any) => {
    // Cache successful GET responses
    if (
      response.config.method === 'get' &&
      response.status === 200 &&
      response.config.cache !== false
    ) {
      const cacheKey = apiCache.generateKey(response.config.url, response.config.params);
      apiCache.set(cacheKey, response.data, response.config.cacheTTL);
    }
    return response;
  });
};