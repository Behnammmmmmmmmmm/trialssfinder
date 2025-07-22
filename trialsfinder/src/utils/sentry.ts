import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';

export const initSentry = () => {
  if (process.env.NODE_ENV === 'production' || process.env.REACT_APP_SENTRY_DSN) {
    Sentry.init({
      dsn: process.env.REACT_APP_SENTRY_DSN || "https://6a27513d3e5b33996570af2d2da16310@o4509711519186949.ingest.de.sentry.io/4509711520694352",
      integrations: [
        new BrowserTracing({
          routingInstrumentation: Sentry.reactRouterV6Instrumentation(
            window.history
          ),
          tracePropagationTargets: [
            'localhost',
            /^https:\/\/yourserver\.io\/api/,
            /^https:\/\/api\.trialsfinder\.com/,
          ],
        }),
      ],
      tracesSampleRate: 0.1,
      environment: process.env.REACT_APP_ENVIRONMENT || 'production',
      release: process.env.REACT_APP_VERSION || '1.0.0',
      normalizeDepth: 10,
      attachStacktrace: true,
      autoSessionTracking: true,
      maxBreadcrumbs: 50,
      sendDefaultPii: true,
      beforeSend(event, hint) {
        // Filter out local development errors
        if (window.location.hostname === 'localhost' && process.env.NODE_ENV !== 'production') {
          return null;
        }
        
        // Filter sensitive data
        if (event.request?.cookies) {
          delete event.request.cookies;
        }
        
        if (event.extra) {
          const sensitiveKeys = ['password', 'token', 'secret', 'api_key'];
          Object.keys(event.extra).forEach(key => {
            if (sensitiveKeys.some(sensitive => key.toLowerCase().includes(sensitive))) {
              event.extra![key] = '[FILTERED]';
            }
          });
        }
        
        return event;
      },
      ignoreErrors: [
        // Browser extensions
        'top.GLOBALS',
        // Random plugins/extensions
        'originalCreateNotification',
        'canvas.contentDocument',
        'MyApp_RemoveAllHighlights',
        'http://tt.epicplay.com',
        "Can't find variable: ZiteReader",
        'jigsaw is not defined',
        'ComboSearch is not defined',
        'http://loading.retry.widdit.com/',
        'atomicFindClose',
        // Facebook related
        'fb_xd_fragment',
        // Other plugins
        'bmi_SafeAddOnload',
        'EBCallBackMessageReceived',
        // Google related
        'google',
        'GoogleAnalyticsObject',
        // Network errors
        'Network request failed',
        'NetworkError',
        'Failed to fetch',
        // Misc
        'Non-Error promise rejection captured',
        'ResizeObserver loop limit exceeded',
        'ResizeObserver loop completed with undelivered notifications',
      ],
      denyUrls: [
        // Facebook
        /graph\.facebook\.com/i,
        // Chrome extensions
        /extensions\//i,
        /^chrome:\/\//i,
        /^chrome-extension:\/\//i,
        // Other
        /127\.0\.0\.1:4001\/isrunning/i,
        /webappstoolbarba\.texthelp\.com\//i,
        /metrics\.itunes\.apple\.com\.edgesuite\.net\//i,
      ],
    });
  }
};

export const captureException = (error: Error, context?: Record<string, any>) => {
  if (process.env.NODE_ENV === 'production') {
    Sentry.captureException(error, {
      contexts: {
        custom: context || {},
      },
    });
  } else {
    console.error('Error captured:', error, context);
  }
};

export const setUser = (user: { id: string | number; username?: string; email?: string } | null) => {
  if (process.env.NODE_ENV === 'production') {
    Sentry.setUser(user);
  }
};

export const addBreadcrumb = (breadcrumb: Sentry.Breadcrumb) => {
  if (process.env.NODE_ENV === 'production') {
    Sentry.addBreadcrumb(breadcrumb);
  }
};