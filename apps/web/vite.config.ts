import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    watch: {
      ignored: ['**/dist_app/**', '**/dist_installer/**', '**/build/**', '**/venv/**']
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        configure: (proxy) => {
          // Gracefully suppress ECONNREFUSED terminal noise while backend is starting up
          process.nextTick(() => {
            const originalListeners = proxy.rawListeners('error');
            proxy.removeAllListeners('error');
            proxy.on('error', (err: any, _req: any, res: any) => {
              if (err && err.code === 'ECONNREFUSED') {
                if (res && !res.headersSent && typeof res.writeHead === 'function') {
                  res.writeHead(503, {
                    'Content-Type': 'application/json',
                    'Retry-After': '1',
                  });
                  res.end(JSON.stringify({
                    error: 'Backend API is still starting up. Please wait...',
                    status: 503,
                    starting: true
                  }));
                }
                return;
              }
              for (const listener of originalListeners) {
                (listener as any)(err, _req, res);
              }
            });
          });
        }
      },
      '/docs': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/redoc': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/openapi.json': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    }
  }
})

