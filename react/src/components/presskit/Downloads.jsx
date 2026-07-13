import React from 'react'
import { motion } from 'framer-motion'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.2,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      ease: [0.16, 1, 0.3, 1],
    },
  },
}

const PRESSKIT_DRIVE_URL =
  'https://drive.google.com/file/d/1o_ODH3OizxgFXNNM5PLdVOC0Ww4r7hEf/view?usp=drivesdk'

export default function Downloads() {
  return (
    <motion.section
      id="downloads"
      className="presskit-section"
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-100px' }}
    >
      <motion.div
        className="section-heading"
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: '-100px' }}
      >
        <motion.h2 variants={itemVariants}>Descargas</motion.h2>
        <motion.div className="minimal-line" variants={itemVariants} />
      </motion.div>

      <motion.div className="presskit-downloads-grid" variants={itemVariants}>
        <motion.a
          href={PRESSKIT_DRIVE_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="presskit-download-btn"
          variants={itemVariants}
          whileTap={{ scale: 0.98 }}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          Press Kit (Google Drive)
        </motion.a>
      </motion.div>
    </motion.section>
  )
}