import { resolve } from 'path';
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import liveReload from 'vite-plugin-live-reload';

export default defineConfig(() => ({
  base: '/static/dist/',

  resolve: {
    alias: {
      '@': resolve(import.meta.dirname, './assets/js/'),
    },
  },

  build: {
    outDir: './static/dist',
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        common: 'assets/js/common.js',
      },
    },
  },

  plugins: [tailwindcss(), liveReload(['**/templates/**/*.html'])],

  server: {
    port: 3000,
    // Do not use another port if 3000 is busy, its hardcoded elsewhere and required to work properly
    strictPort: true,
    host: true,
    allowedHosts: ['{{ cookiecutter.project_slug|replace("_", "-") }}.docker.test'],
    proxy: {
      '^(?!/static/dist/)': {
        target: 'http://backend.{{ cookiecutter.__network_name }}:8000',
      },
    },
    watch: {
      awaitWriteFinish: {
        stabilityThreshold: 500,
      },
      ignored: [
        '**/.vite/**',
        '**/__pycache__/**',
        '**/*.py',
        '**/*.pyc',
        '**/.venv/**',
        '**/.direnv/**',
        '**/.devenv/**',
        '**/.mypy_cache/**',
        '**/media/**',
        '**/static/**',
        '**/node_modules/**',
        '**/tests/**',
      ],
    },
  },
}));
