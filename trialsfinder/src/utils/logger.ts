interface LogLevel {
  value: number;
  label: string;
}

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  context?: Record<string, any>;
  error?: Error;
}

class Logger {
  private static instance: Logger;
  private logBuffer: LogEntry[] = [];
  private maxBufferSize = 100;
  private flushInterval = 30000; // 30 seconds
  private endpoint = '/api/logs/';

  private logLevels: Record<string, LogLevel> = {
    DEBUG: { value: 0, label: 'DEBUG' },
    INFO: { value: 1, label: 'INFO' },
    WARN: { value: 2, label: 'WARN' },
    ERROR: { value: 3, label: 'ERROR' },
  };

  private currentLevel: LogLevel = this.logLevels.INFO;

  private constructor() {
    this.setupPeriodicFlush();
    this.setupUnloadFlush();
  }

  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  setLevel(level: keyof typeof Logger.prototype.logLevels): void {
    this.currentLevel = this.logLevels[level];
  }

  debug(message: string, context?: Record<string, any>): void {
    this.log(this.logLevels.DEBUG, message, context);
  }

  info(message: string, context?: Record<string, any>): void {
    this.log(this.logLevels.INFO, message, context);
  }

  warn(message: string, context?: Record<string, any>): void {
    this.log(this.logLevels.WARN, message, context);
  }

  error(message: string, context?: Record<string, any>): void {
    this.log(this.logLevels.ERROR, message, context);
  }

  private log(level: LogLevel, message: string, context?: Record<string, any>): void {
    if (level.value < this.currentLevel.value) {
      return;
    }

    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level: level.label,
      message,
      context: {
        ...context,
        userAgent: navigator.userAgent,
        url: window.location.href,
        sessionId: this.getSessionId(),
      },
    };

    // Console log in development
    if (process.env.NODE_ENV === 'development') {
      const logMethod = level.label.toLowerCase() as 'debug' | 'info' | 'warn' | 'error';
      console[logMethod](message, context);
    }

    this.logBuffer.push(entry);

    if (this.logBuffer.length >= this.maxBufferSize) {
      this.flush();
    }
  }

  private getSessionId(): string {
    let sessionId = sessionStorage.getItem('sessionId');
    if (!sessionId) {
      sessionId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('sessionId', sessionId);
    }
    return sessionId;
  }

  private setupPeriodicFlush(): void {
    setInterval(() => {
      if (this.logBuffer.length > 0) {
        this.flush();
      }
    }, this.flushInterval);
  }

  private setupUnloadFlush(): void {
    window.addEventListener('beforeunload', () => {
      if (this.logBuffer.length > 0) {
        this.flush(true);
      }
    });
  }

  private async flush(sync = false): Promise<void> {
    if (this.logBuffer.length === 0) {
      return;
    }

    const logs = [...this.logBuffer];
    this.logBuffer = [];

    const payload = JSON.stringify({ logs });

    if (sync) {
      // Use sendBeacon for synchronous sending on page unload
      try {
        navigator.sendBeacon(this.endpoint, payload);
      } catch (error) {
        // Silently fail for sendBeacon
      }
    } else {
      try {
        const response = await fetch(this.endpoint, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCookie('csrftoken') || ''
          },
          credentials: 'include',
          body: payload,
        });
        
        if (!response.ok && response.status !== 400) {
          // Re-add logs to buffer if sending failed (except for bad requests)
          this.logBuffer.unshift(...logs);
        }
      } catch (error) {
        // Re-add logs to buffer if sending failed
        this.logBuffer.unshift(...logs);
        
        // Log to console in development
        if (process.env.NODE_ENV === 'development') {
          console.error('Failed to send logs:', error);
        }
      }
    }
  }

  private getCookie(name: string): string | null {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
      return parts.pop()?.split(';').shift() || null;
    }
    return null;
  }
}

// Export singleton instance
export const logger = Logger.getInstance();

// Make logger available globally for error handlers
declare global {
  interface Window {
    logger: Logger;
    currentUser?: { username: string };
  }
}

window.logger = logger;