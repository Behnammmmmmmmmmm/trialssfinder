// utils/performanceOptimizations.js

// Resource hints for critical resources
export const addResourceHints = () => {
  const head = document.head;
  
  // Preconnect to API
  const apiPreconnect = document.createElement('link');
  apiPreconnect.rel = 'preconnect';
  apiPreconnect.href = 'https://api.trialsfinder.com';
  head.appendChild(apiPreconnect);
  
  // DNS prefetch for third-party services
  const dnsPrefetch = document.createElement('link');
  dnsPrefetch.rel = 'dns-prefetch';
  dnsPrefetch.href = 'https://www.google-analytics.com';
  head.appendChild(dnsPrefetch);
};

// Progressive image loading
export const progressiveImageLoading = () => {
  const images = document.querySelectorAll('img[data-src]');
  
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target as HTMLImageElement;
        
        // Load low quality placeholder first
        if (img.dataset.placeholder) {
          img.src = img.dataset.placeholder;
        }
        
        // Load full image
        const fullImage = new Image();
        fullImage.onload = () => {
          img.src = fullImage.src;
          img.classList.add('loaded');
        };
        fullImage.src = img.dataset.src!;
        
        img.removeAttribute('data-src');
        observer.unobserve(img);
      }
    });
  }, {
    rootMargin: '50px 0px',
    threshold: 0.01
  });
  
  images.forEach(img => imageObserver.observe(img));
};

// Font optimization
export const optimizeFontLoading = () => {
  // Use font-display: swap
  const style = document.createElement('style');
  style.textContent = `
    @font-face {
      font-family: 'Inter';
      font-display: swap;
      src: local('Inter'),
           url('/fonts/inter-var.woff2') format('woff2-variations'),
           url('/fonts/inter-regular.woff2') format('woff2');
    }
  `;
  document.head.appendChild(style);
};

// Reduce JavaScript execution time
export const deferNonCriticalScripts = () => {
  // Defer analytics
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      // Load Google Analytics
      const script = document.createElement('script');
      script.async = true;
      script.src = 'https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID';
      document.head.appendChild(script);
    });
  }
};

// Optimize React rendering
export const optimizeReactPerformance = () => {
  // Enable React Profiler in development
  if (process.env.NODE_ENV === 'development') {
    const { unstable_trace: trace } = require('scheduler/tracing');
    
    window.__REACT_DEVTOOLS_GLOBAL_HOOK__ = {
      ...window.__REACT_DEVTOOLS_GLOBAL_HOOK__,
      onCommitFiberRoot: (id: any, root: any) => {
        // Log slow renders
        const renderTime = root.actualDuration;
        if (renderTime > 16) { // More than one frame
          console.warn(`Slow render detected: ${renderTime}ms`);
        }
      }
    };
  }
};

// Minimize main thread work
export const optimizeMainThread = () => {
  // Use Web Workers for heavy computations
  if ('Worker' in window) {
    const worker = new Worker('/workers/search-worker.js');
    
    // Offload search filtering to worker
    window.searchWorker = worker;
  }
  
  // Use requestAnimationFrame for DOM updates
  const scheduleUpdate = (callback: () => void) => {
    if ('requestIdleCallback' in window) {
      requestIdleCallback(callback, { timeout: 2000 });
    } else {
      requestAnimationFrame(callback);
    }
  };
  
  window.scheduleUpdate = scheduleUpdate;
};

// Reduce layout shifts
export const preventLayoutShifts = () => {
  // Add aspect ratio to images
  const images = document.querySelectorAll('img:not([height])');
  images.forEach(img => {
    if (img.getAttribute('width')) {
      const width = parseInt(img.getAttribute('width')!);
      const aspectRatio = img.naturalHeight / img.naturalWidth;
      img.setAttribute('height', String(Math.round(width * aspectRatio)));
    }
  });
  
  // Reserve space for dynamic content
  const dynamicContainers = document.querySelectorAll('[data-dynamic-height]');
  dynamicContainers.forEach(container => {
    const minHeight = container.getAttribute('data-dynamic-height');
    (container as HTMLElement).style.minHeight = minHeight + 'px';
  });
};

// Initialize all optimizations
export const initializePerformanceOptimizations = () => {
  // Run immediately
  addResourceHints();
  optimizeFontLoading();
  preventLayoutShifts();
  
  // Run after DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      progressiveImageLoading();
      optimizeMainThread();
    });
  } else {
    progressiveImageLoading();
    optimizeMainThread();
  }
  
  // Run after page load
  window.addEventListener('load', () => {
    deferNonCriticalScripts();
    optimizeReactPerformance();
  });
};