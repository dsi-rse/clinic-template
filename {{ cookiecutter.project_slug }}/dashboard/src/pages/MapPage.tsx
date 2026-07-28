import { useRef, useEffect } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { useQuery } from '../lib/useQuery'

interface CityPoint {
  city: string
  lat: number
  lon: number
  avg_value: number
}

export default function MapPage() {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<maplibregl.Map | null>(null)

  const { data: points } = useQuery<CityPoint>(
    `SELECT city, lat, lon, AVG(value) AS avg_value FROM demo GROUP BY city, lat, lon`,
  )

  useEffect(() => {
    if (!mapRef.current) return
    const map = new maplibregl.Map({
      container: mapRef.current,
      style: 'https://demotiles.maplibre.org/style.json',
      center: [-98.5795, 39.8283],
      zoom: 3,
    })
    mapInstanceRef.current = map
    return () => map.remove()
  }, [])

  useEffect(() => {
    const map = mapInstanceRef.current
    if (!map || !points) return

    const addMarkers = () => {
      points.forEach((pt) => {
        new maplibregl.Marker()
          .setLngLat([pt.lon, pt.lat])
          .setPopup(
            new maplibregl.Popup().setHTML(
              `<b>${pt.city}</b><br>Avg value: ${pt.avg_value.toFixed(2)}`,
            ),
          )
          .addTo(map)
      })
    }

    if (map.loaded()) {
      addMarkers()
    } else {
      map.on('load', addMarkers)
    }
  }, [points])

  return (
    <div style={{ padding: '1rem' }}>
      <h1>Map</h1>
      <div ref={mapRef} style={{ width: '100%', height: '500px' }} />
    </div>
  )
}
