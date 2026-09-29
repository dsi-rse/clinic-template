import { useRef, useEffect } from 'react'
import * as Plot from '@observablehq/plot'

interface PlotFigureProps {
  options: Plot.PlotOptions
}

export default function PlotFigure({ options }: PlotFigureProps) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!ref.current) return
    const plot = Plot.plot(options)
    ref.current.replaceChildren(plot)
    return () => plot.remove()
  }, [options])

  return <div ref={ref} />
}
