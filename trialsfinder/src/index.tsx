import React from 'react';
import ReactDOM from 'react-dom/client';

// Get root element
const rootElement = document.getElementById('root');
if (!rootElement) {
  console.error('Failed to find the root element');
  throw new Error('Failed to find the root element');
}

console.log('Root element found, creating React root...');

// Create root
const root = ReactDOM.createRoot(rootElement);

// Simple test render
root.render(
  <div style={{ padding: '20px' }}>
    <h1>TrialsFinder is loading...</h1>
    <p>If you see this, React is working!</p>
  </div>
);

// Load styles
import('./styles/index.css').catch(console.error);

// Load the app
setTimeout(() => {
  console.log('Loading main app...');
  import('./App')
    .then(({ default: App }) => {
      console.log('App loaded, rendering...');
      root.render(
        <React.StrictMode>
          <App />
        </React.StrictMode>
      );
    })
    .catch(error => {
      console.error('Failed to load app:', error);
      root.render(
        <div style={{ padding: '20px', color: 'red' }}>
          <h1>Error Loading App</h1>
          <pre>{error.toString()}</pre>
        </div>
      );
    });
}, 100);