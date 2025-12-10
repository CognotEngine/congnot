import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { I18nProvider } from './contexts/I18nContext.tsx'
import { ReactFlowProvider } from 'reactflow'

const root = document.getElementById('root')
if (root) {
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <I18nProvider>
        <ReactFlowProvider>
          <App />
        </ReactFlowProvider>
      </I18nProvider>
    </React.StrictMode>,
  )
}
