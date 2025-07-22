// Browser-compatible fetch implementation
// This replaces cross-fetch/node-fetch with native browser fetch

const browserFetch = typeof window !== 'undefined' && window.fetch 
  ? window.fetch.bind(window) 
  : null;

if (!browserFetch) {
  throw new Error('Native fetch is not available');
}

// Export both default and named exports for compatibility
export default browserFetch;
export { browserFetch as fetch };

// Add polyfill for older browsers if needed
if (typeof window !== 'undefined' && !window.fetch) {
  console.warn('Fetch API not available, some features may not work');
}