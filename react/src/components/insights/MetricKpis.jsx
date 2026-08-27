import React from 'react'
import { motion } from 'framer-motion'

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] },
  },
}

export default function MetricKpis({ kpis }) {
  if (!kpis) return null

  const cards = [
    {
      label: 'Audiencia Total',
      value: (kpis.facebook_followers + kpis.instagram_followers).toLocaleString(),
      detail: `${kpis.facebook_followers.toLocaleString()} FB · ${kpis.instagram_followers.toLocaleString()} IG`,
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
          <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
      ),
      highlight: true,
    },
    {
      label: 'Visualizaciones Totales',
      value: kpis.total_views.toLocaleString(),
      detail: `${kpis.total_reach.toLocaleString()} cuentas alcanzadas`,
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="23 7 16 12 23 17 23 7" />
          <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
        </svg>
      ),
    },
    {
      label: 'Interacciones Totales',
      value: kpis.total_interactions.toLocaleString(),
      detail: `${kpis.total_analyzed_posts} publicaciones analizadas`,
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3" />
        </svg>
      ),
    },
    {
      label: 'Promedio de Interacción',
      value: `${kpis.avg_interactions_per_post}`,
      detail: 'Reacciones y comentarios / post',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="18" y1="20" x2="18" y2="10" />
          <line x1="12" y1="20" x2="12" y2="4" />
          <line x1="6" y1="20" x2="6" y2="14" />
        </svg>
      ),
    },
  ]

  return (
    <div className="insights-kpi-grid">
      {cards.map((card, idx) => (
        <motion.div
          key={idx}
          className={`insights-kpi-card ${card.highlight ? 'kpi-highlight' : ''}`}
          variants={itemVariants}
        >
          <div className="kpi-icon-wrapper">{card.icon}</div>
          <div className="kpi-info">
            <span className="kpi-label">{card.label}</span>
            <span className="kpi-value">{card.value}</span>
            <span className="kpi-detail">{card.detail}</span>
          </div>
        </motion.div>
      ))}
    </div>
  )
}
