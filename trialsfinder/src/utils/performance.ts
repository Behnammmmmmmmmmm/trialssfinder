// Image lazy loading with Intersection Observer
export const lazyLoadImages = () => {
  const images = document.querySelectorAll('img[data-src]');
  
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target as HTMLImageElement;
        
        // Set loading attribute for native lazy loading
        img.loading = 'lazy';
        
        // Load the image
        img.src = img.dataset.src!;
        img.removeAttribute('data-src');
        
        // Add dimensions to prevent layout shift
        if (!img.hasAttribute('width') && img.naturalWidth) {
          img.width = img.naturalWidth;
        }
        if (!img.hasAttribute('height') && img.naturalHeight) {
          img.height = img.naturalHeight;
        }
        
        observer.unobserve(img);
      }
    });
  }, {
    rootMargin: '50px 0px',
    threshold: 0.01
  });
  
  images.forEach(img => imageObserver.observe(img));
};

// Debounce for search inputs
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: ReturnType<typeof setTimeout>;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

// Virtual scrolling helper
export class VirtualScroller<T> {
  private items: T[];
  private itemHeight: number;
  private containerHeight: number;
  private overscan: number;

  constructor(items: T[], itemHeight: number, containerHeight: number, overscan = 3) {
    this.items = items;
    this.itemHeight = itemHeight;
    this.containerHeight = containerHeight;
    this.overscan = overscan;
  }

  getVisibleItems(scrollTop: number): { items: T[], startIndex: number, endIndex: number } {
    const startIndex = Math.max(0, Math.floor(scrollTop / this.itemHeight) - this.overscan);
    const endIndex = Math.min(
      this.items.length - 1,
      Math.ceil((scrollTop + this.containerHeight) / this.itemHeight) + this.overscan
    );

    return {
      items: this.items.slice(startIndex, endIndex + 1),
      startIndex,
      endIndex
    };
  }

  getTotalHeight(): number {
    return this.items.length * this.itemHeight;
  }
}

// Prefetch critical resources
export const prefetchResources = () => {
  const criticalResources = [
    '/api/trials/',
    '/api/industries/',
  ];
  
  criticalResources.forEach(resource => {
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = resource;
    link.as = 'fetch';
    link.crossOrigin = 'anonymous';
    document.head.appendChild(link);
  });
};

// Optimize long tasks
export const runAfterIdle = (callback: () => void) => {
  if ('requestIdleCallback' in window) {
    window.requestIdleCallback(callback, { timeout: 2000 });
  } else {
    setTimeout(callback, 1);
  }
};
