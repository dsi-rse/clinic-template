import type { ReactNode } from 'react'

interface CardProps {
  title: string
  children: ReactNode
  // flex-basis controls the grid: '1 1 100%' = full row, default = half row
  flex?: string
}

export default function Card({ title, children, flex = '1 1 480px' }: CardProps) {
  return (
    <figure
      style={{
        margin: 0,
        flex,
        minWidth: 0,
        background: '#fcfcfb',
        border: '1px solid rgba(11, 11, 11, 0.1)',
        borderRadius: 8,
        padding: '12px 16px 8px',
      }}
    >
      <figcaption style={{ fontSize: 14, fontWeight: 600, color: '#0b0b0b', marginBottom: 8 }}>
        {title}
      </figcaption>
      {children}
    </figure>
  )
}
