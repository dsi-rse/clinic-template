import React from 'react'
import ReactDOM from 'react-dom/client'
import { Provider, defaultTheme } from '@adobe/react-spectrum'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* colorScheme pinned to light: Plot charts and MapLibre don't follow the OS theme */}
    <Provider theme={defaultTheme} colorScheme="light">
      <App />
    </Provider>
  </React.StrictMode>,
)
