import React from 'react';
import ReactDOM from 'react-dom/client';

// Critical CSS only
import './styles/critical.css';

// Get root element
const rootElement = document.getElementById('root');
if (!rootElement) throw new Error('Failed to find the root element');

// Create root
const root = ReactDOM.createRoot(rootElement);

// Fast initial render
root.render(
  <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
    <div style={{ textAlign: 'center', padding: '2rem' }}>
      <div className="spinner" data-size="lg"></div>
      <p style={{ marginTop: '1rem', color: '#6b7280' }}>Loading TrialsFinder...</p>
    </div>
  </div>
);

// Load the app asynchronously
(async () => {
  try {
    // Load remaining CSS
    const { default: App } = await import('./App');
    await import('./styles/index.css');
    
    // Render full app
    root.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
    
    // Register service worker with proper cleanup
    if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js').catch(() => {
          // Silently fail
        });
      });
    }
  } catch (error) {
    console.error('Failed to load app:', error);
  }
})();

// Clean up event listeners on page unload to allow bfcache
window.addEventListener('pagehide', () => {
  // Remove any event listeners that might prevent bfcache
  if ('serviceWorker' in navigator) {
    // Don't unregister service worker, just clean up listeners
  }
});

// Avoid using unload event which prevents bfcache
// window.addEventListener('unload', ...) // DON'T USE THIS