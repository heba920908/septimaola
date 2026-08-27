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

export default function TopPostsSection({ topPosts }) {
  if (!topPosts || topPosts.length === 0) return null

  return (
    <motion.div
      className="insights-top-posts-section"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
    >
      <div className="section-header-row">
        <div>
          <h3>Publicaciones de Mayor Impacto y Patrones</h3>
          <p className="section-subtitle">
            Formatos y contenidos que generaron mayor alcance, reproducciones y viralidad
          </p>
        </div>
      </div>

      <div className="top-posts-grid">
        {topPosts.map((post, idx) => (
          <div
            key={post.id || idx}
            className="top-post-card"
          >
            <div className="post-header-row">
              <span className={`platform-pill ${post.platform}`}>
                {post.platform === 'instagram' ? 'Instagram' : 'Facebook'}
              </span>
              <span className="post-timestamp">
                {post.timestamp ? post.timestamp.split('T')[0] : ''}
              </span>
            </div>

            <div className="post-patterns-list">
              {post.patterns &&
                post.patterns.map((tag, tIdx) => (
                  <span key={tIdx} className="pattern-badge">
                    #{tag}
                  </span>
                ))}
            </div>

            <p className="post-caption-text">
              {post.caption
                ? post.caption.length > 180
                  ? post.caption.slice(0, 180) + '...'
                  : post.caption
                : 'Sin texto de descripción'}
            </p>

            <div className="post-stats-row">
              {post.views !== null && post.views > 0 && (
                <div className="stat-item">
                  <span className="stat-label">Views</span>
                  <span className="stat-value">{post.views.toLocaleString()}</span>
                </div>
              )}
              {post.reach !== null && post.reach > 0 && (
                <div className="stat-item">
                  <span className="stat-label">Alcance</span>
                  <span className="stat-value">{post.reach.toLocaleString()}</span>
                </div>
              )}
              <div className="stat-item">
                <span className="stat-label">Likes</span>
                <span className="stat-value">{post.like_count || 0}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Comentarios</span>
                <span className="stat-value">{post.comments_count || 0}</span>
              </div>
            </div>

            {post.permalink && (
              <a
                href={post.permalink}
                target="_blank"
                rel="noopener noreferrer"
                className="post-link-btn"
              >
                Ver publicación ↗
              </a>
            )}
          </div>
        ))}
      </div>
    </motion.div>
  )
}
