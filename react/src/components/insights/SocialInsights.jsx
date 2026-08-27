import React from 'react'
import { motion } from 'framer-motion'
import MetricKpis from './MetricKpis'
import TimeSeriesGraph from './TimeSeriesGraph'
import AgendaCorrelation from './AgendaCorrelation'
import TopPostsSection from './TopPostsSection'
import RecommendationsSection from './RecommendationsSection'

import defaultInsightsData from '../../data/insights-data.json'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.12,
      delayChildren: 0.1,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 25 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.16, 1, 0.3, 1],
    },
  },
}

export default function SocialInsights() {
  const handleBackClick = (e) => {
    e.preventDefault()
    window.location.hash = ''
  }

  const data = defaultInsightsData || {}

  return (
    <div className="insights-page">
      <div className="insights-header">
        <div className="container">
          <motion.div className="back-link-container" variants={itemVariants}>
            <a href="#/" onClick={handleBackClick} className="back-link">
              ← Volver
            </a>
          </motion.div>

          <motion.div
            className="section-heading"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            <motion.h1 variants={itemVariants}>Métricas e Insights Sociales</motion.h1>
            <motion.div className="minimal-line" variants={itemVariants} />
          </motion.div>

          <motion.p className="impact-phrase" variants={itemVariants}>
            Analítica de rendimiento digital, tracción de agenda y recomendaciones estratégicas
          </motion.p>
        </div>
      </div>

      <div className="container insights-content-body">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Top Level KPIs */}
          <MetricKpis kpis={data.kpis} />

          {/* Time Series Graph */}
          <TimeSeriesGraph timeSeries={data.time_series} />

          {/* Agenda vs Social Correlation */}
          <AgendaCorrelation correlations={data.agenda_correlations} />

          {/* Top Posts & Content Patterns */}
          <TopPostsSection topPosts={data.top_posts} />

          {/* AI / Heuristic Strategic Recommendations */}
          <RecommendationsSection aiAnalysis={data.ai_analysis} />
        </motion.div>
      </div>
    </div>
  )
}
