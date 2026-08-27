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

export default function RecommendationsSection({ aiAnalysis }) {
  if (!aiAnalysis) return null

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'Formato':
        return '🎬'
      case 'Colaboraciones':
        return '🤝'
      case 'Timing':
        return '⏱️'
      default:
        return '💡'
    }
  }

  return (
    <motion.div
      className="insights-recommendations-section"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
    >
      <div className="section-header-row">
        <div>
          <h3>Recomendaciones Estratégicas &amp; Síntesis</h3>
          <p className="section-subtitle">
            Conclusiones analíticas accionables para potenciar el crecimiento y engagement de la banda
          </p>
        </div>
      </div>

      {/* Executive Summary Card */}
      <div className="executive-summary-card">
        <div className="summary-badge">Resumen Ejecutivo</div>
        <p className="summary-text">{aiAnalysis.executive_summary}</p>

        {aiAnalysis.key_patterns && aiAnalysis.key_patterns.length > 0 && (
          <div className="key-patterns-box">
            <h5>Patrones Clave Detectados:</h5>
            <ul>
              {aiAnalysis.key_patterns.map((pat, idx) => (
                <li key={idx}>{pat}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Recommendations Cards Grid */}
      <div className="recommendations-grid">
        {aiAnalysis.recommendations &&
          aiAnalysis.recommendations.map((rec, idx) => (
            <div
              key={idx}
              className="recommendation-card"
            >
              <div className="rec-header">
                <span className="rec-icon">{getCategoryIcon(rec.category)}</span>
                <span className="rec-category">{rec.category}</span>
              </div>
              <h4 className="rec-title">{rec.title}</h4>
              <p className="rec-description">{rec.description}</p>
            </div>
          ))}
      </div>
    </motion.div>
  )
}
