import { Routes, Route, Link } from 'react-router-dom'
import OverviewPage from './pages/OverviewPage'
import MapPage from './pages/MapPage'

export default function App() {
  return (
    <div>
      <nav>
        <Link to="/">Overview</Link>
        {' | '}
        <Link to="/map">Map</Link>
      </nav>
      <Routes>
        <Route path="/" element={<OverviewPage />} />
        <Route path="/map" element={<MapPage />} />
      </Routes>
    </div>
  )
}
