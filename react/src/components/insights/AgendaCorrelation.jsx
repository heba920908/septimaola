import React, { useState } from 'react'
import { motion } from 'framer-motion'

const itemVariants = {
  hidden: { opacity: 0, y: 15 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] },
  },
}

export default function AgendaCorrelation({ correlations }) {
  const [filter, setFilter] = useState('all')

  if (!correlations || correlations.length === 0) return null

  const filtered = correlations.filter((item) => {
    if (filter === 'high') return item.traction_score === 'Alto'
    if (filter === 'foro-bar') return ['Foro', 'Bar'].includes(item.event_type)
    if (filter === 'cultural-fest') return ['Cultural', 'Festival', 'Familiar'].includes(item.event_type)
    return true
  })

  const getBadgeClass = (score) => {
    switch (score) {
      case 'Alto':
        return 'traction-badge high'
      case 'Medio':
        return 'traction-badge medium'
      default:
        return 'traction-badge moderate'
    }
  }

  return (
    <motion.div
      className="insights-agenda-section"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    >
      <div className="section-header-row">
        <div>
          <h3>Correlación de Agenda &amp; Tracción Social</h3>
          <p className="section-subtitle">
            Impacto digital y respuesta de la audiencia en fechas de presentaciones en vivo
          </p>
        </div>

        <div className="agenda-filters">
          <button
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            Todos ({correlations.length})
          </button>
          <button
            className={`filter-btn ${filter === 'high' ? 'active' : ''}`}
            onClick={() => setFilter('high')}
          >
            Alta Tracción
          </button>
          <button
            className={`filter-btn ${filter === 'foro-bar' ? 'active' : ''}`}
            onClick={() => setFilter('foro-bar')}
          >
            Foros y Bares
          </button>
          <button
            className={`filter-btn ${filter === 'cultural-fest' ? 'active' : ''}`}
            onClick={() => setFilter('cultural-fest')}
          >
            Culturales
          </button>
        </div>
      </div>

      <div className="agenda-cards-grid">
        {filtered.map((item, idx) => (
          <div
            key={idx}
            className="agenda-corr-card"
          >
            <div className="card-top">
              <span className="event-date">{item.event_date}</span>
              <span className={getBadgeClass(item.traction_score)}>
                Tracción {item.traction_score}
              </span>
            </div>

            <h4 className="event-title">{item.event_title}</h4>
            <p className="event-venue">📍 {item.event_venue}</p>

            <div className="event-metrics-row">
              <div className="metric-pill">
                <span>Posts:</span> <strong>{item.correlated_posts_count}</strong>
              </div>
              <div className="metric-pill">
                <span>Alcance:</span> <strong>{item.total_reach.toLocaleString()}</strong>
              </div>
              <div className="metric-pill">
                <span>Views:</span> <strong>{item.total_views.toLocaleString()}</strong>
              </div>
              <div className="metric-pill">
                <span>Interacciones:</span> <strong>{item.total_interactions.toLocaleString()}</strong>
              </div>
            </div>

            {item.highlight_caption && (
              <p className="highlight-caption">
                💬 <em>«{item.highlight_caption}»</em>
              </p>
            )}
          </div>
        ))}
      </div>
    </motion.div>
  )
}
