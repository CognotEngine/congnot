import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import dts from 'vite-plugin-dts'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'

// Get __dirname equivalent in ESM
const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export default defineConfig(({ mode }) => {
  const isLibraryBuild = mode === 'library'

  return {
    plugins: [
      react(),
      isLibraryBuild && dts({
        insertTypesEntry: true,
        rollupTypes: true,
      })
    ],
    server: {
      host: '127.0.0.1',
      port: 3000,
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8080',
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api/, '')
        },
        '/models': {
          target: 'http://127.0.0.1:8080',
          changeOrigin: true,
          secure: false
        },
        '/nodes': {
          target: 'http://127.0.0.1:8080',
          changeOrigin: true,
          secure: false
        },
        '/files': {
          target: 'http://127.0.0.1:8080',
          changeOrigin: true,
          secure: false
        },
        '/execution': {
          target: 'http://127.0.0.1:8080',
          changeOrigin: true,
          secure: false
        },
        '/queue': {
          target: 'http://127.0.0.1:8080',
          changeOrigin: true,
          secure: false
        }
      }
    },
    ...(isLibraryBuild && {
      build: {
        lib: {
          entry: resolve(__dirname, 'src/index.ts'),
          name: 'CognotFlowCanvas',
          formats: ['es', 'umd'],
          fileName: (format) => `cognot-flow-canvas.${format}.js`,
        },
        rollupOptions: {
          external: ['react', 'react-dom'],
          output: {
            globals: {
              react: 'React',
              'react-dom': 'ReactDOM',
            },
          },
        },
        cssCodeSplit: true,
        sourcemap: true,
      }
    })
  }
})
