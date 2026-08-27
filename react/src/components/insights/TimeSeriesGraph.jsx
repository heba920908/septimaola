import React, { useState } from 'react'
import { motion } from 'framer-motion'

export default function TimeSeriesGraph({ timeSeries }) {
  const [activeMetric, setActiveMetric] = useState('views')
  const [hoveredIndex, setHoveredIndex] = useState(null)

  if (!timeSeries || timeSeries.length === 0) return null

  const metricsConfig = {
    views: {
      label: 'Visualizaciones',
      color: 'var(--accent)',
      gradientId: 'viewsGrad',
      getValue: (p) => p.views || 0,
    },
    reach: {
      label: 'Alcance',
      color: 'var(--accent-orange)',
      gradientId: 'reachGrad',
      getValue: (p) => p.reach || 0,
    },
    interactions: {
      label: 'Interacciones',
      color: '#4ade80',
      gradientId: 'interGrad',
      getValue: (p) => p.interactions || 0,
    },
  }

  const currentConfig = metricsConfig[activeMetric]
  const values = timeSeries.map(currentConfig.getValue)
  const maxVal = Math.max(...values, 10)

  // Chart dimensions
  const svgWidth = 800
  const svgHeight = 240
  const padLeft = 50
  const padRight = 30
  const padTop = 30
  const padBottom = 40

  const chartW = svgWidth - padLeft - padRight
  const chartH = svgHeight - padTop - padBottom

  // Coordinates
  const points = timeSeries.map((item, idx) => {
    const x = padLeft + (idx / Math.max(timeSeries.length - 1, 1)) * chartW
    const y = padTop + chartH - (currentConfig.getValue(item) / maxVal) * chartH
    return { x, y, item, value: currentConfig.getValue(item) }
  })

  const pathD = points.reduce((acc, p, i) => {
    return i === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`
  }, '')

  const areaD = `${pathD} L ${points[points.length - 1].x} ${padTop + chartH} L ${points[0].x} ${padTop + chartH} Z`

  // Y-axis ticks
  const yTicks = [0, Math.round(maxVal * 0.5), maxVal]

  // X-axis label sample (first, middle, last)
  const xLabelsIndices = [
    0,
    Math.floor(timeSeries.length / 2),
    timeSeries.length - 1,
  ]

  return (
    <div className="insights-chart-container">
      <div className="chart-header">
        <div className="chart-title-group">
          <h3>Evolución Temporal de Métricas</h3>
          <p className="chart-subtitle">Rendimiento por fecha de publicación y actividad</p>
        </div>

        <div className="chart-metric-selector">
          {Object.entries(metricsConfig).map(([key, cfg]) => (
            <button
              key={key}
              className={`metric-btn ${activeMetric === key ? 'active' : ''}`}
              onClick={() => {
                setActiveMetric(key)
                setHoveredIndex(null)
              }}
            >
              {cfg.label}
            </button>
          ))}
        </div>
      </div>

      <div className="svg-wrapper">
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          className="timeseries-svg"
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            <linearGradient id={currentConfig.gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={currentConfig.color} stopOpacity="0.45" />
              <stop offset="100%" stopColor={currentConfig.color} stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Grid lines & Y-ticks */}
          {yTicks.map((tick, i) => {
            const yPos = padTop + chartH - (tick / maxVal) * chartH
            return (
              <g key={i}>
                <line
                  x1={padLeft}
                  y1={yPos}
                  x2={svgWidth - padRight}
                  y2={yPos}
                  stroke="rgba(255,255,255,0.08)"
                  strokeDasharray="4 4"
                />
                <text
                  x={padLeft - 10}
                  y={yPos + 4}
                  textAnchor="end"
                  fill="var(--text-muted)"
                  fontSize="11"
                >
                  {tick.toLocaleString()}
                </text>
              </g>
            )
          })}

          {/* Area under curve */}
          <path d={areaD} fill={`url(#${currentConfig.gradientId})`} />

          {/* Line stroke */}
          <path
            d={pathD}
            fill="none"
            stroke={currentConfig.color}
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Data points */}
          {points.map((pt, i) => (
            <g
              key={i}
              className="chart-point"
              onMouseEnter={() => setHoveredIndex(i)}
              onTouchStart={() => setHoveredIndex(i)}
            >
              <circle
                cx={pt.x}
                cy={pt.y}
                r={hoveredIndex === i ? 6 : 4}
                fill={hoveredIndex === i ? '#ffffff' : currentConfig.color}
                stroke="var(--surface)"
                strokeWidth="2"
                style={{ cursor: 'pointer', transition: 'all 0.2s ease' }}
              />
            </g>
          ))}

          {/* X-axis labels */}
          {xLabelsIndices.map((idx) => {
            const pt = points[idx]
            if (!pt) return null
            return (
              <text
                key={idx}
                x={pt.x}
                y={svgHeight - 12}
                textAnchor="middle"
                fill="var(--text-muted)"
                fontSize="11"
              >
                {pt.item.date}
              </text>
            )
          })}
        </svg>

        {/* Floating Tooltip */}
        {hoveredIndex !== null && points[hoveredIndex] && (
          <div
            className="chart-tooltip"
            style={{
              left: `${(points[hoveredIndex].x / svgWidth) * 100}%`,
              top: `${(points[hoveredIndex].y / svgHeight) * 100}%`,
            }}
          >
            <span className="tooltip-date">{points[hoveredIndex].item.date}</span>
            <span className="tooltip-value">
              {currentConfig.label}: <strong>{points[hoveredIndex].value.toLocaleString()}</strong>
            </span>
            <span className="tooltip-meta">
              {points[hoveredIndex].item.posts_count} publicación(es)
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
