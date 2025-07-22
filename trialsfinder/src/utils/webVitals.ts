export const reportWebVitals = () => {
  if ('PerformanceObserver' in window) {
    // LCP
    try {
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        console.log('LCP:', lastEntry.startTime);
        lcpObserver.disconnect();
      });
      lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
    } catch (e) {}

    // FID
    try {
      const fidObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          // Cast to any to access processingStart
          const fidEntry = entry as any;
          if (fidEntry.processingStart) {
            const delay = fidEntry.processingStart - fidEntry.startTime;
            console.log('FID:', delay);
          }
        }
        fidObserver.disconnect();
      });
      fidObserver.observe({ type: 'first-input', buffered: true });
    } catch (e) {}

    // CLS
    try {
      let clsValue = 0;
      let clsEntries: PerformanceEntry[] = [];

      const sessionValue = () => {
        const gaps: number[] = [];
        let prevEntry: any;
        
        clsEntries.forEach((entry: any) => {
          if (!prevEntry || entry.startTime - prevEntry.startTime > 1000) {
            gaps.push(entry.value);
          } else {
            gaps[gaps.length - 1] += entry.value;
          }
          prevEntry = entry;
        });
        
        return Math.max(...gaps, 0);
      };

      const clsObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!(entry as any).hadRecentInput) {
            clsEntries.push(entry);
            clsValue = sessionValue();
          }
        }
      });
      clsObserver.observe({ type: 'layout-shift', buffered: true });

      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden' && clsValue > 0) {
          console.log('CLS:', clsValue);
          clsObserver.disconnect();
        }
      }, { once: true });
    } catch (e) {}
  }
};