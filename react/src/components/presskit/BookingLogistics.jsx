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

export default function BookingLogistics() {
  return (
    <motion.section
      id="booking-logistics"
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
        <motion.h2 variants={itemVariants}>Reservas y Logística</motion.h2>
        <motion.div className="minimal-line" variants={itemVariants} />
      </motion.div>
      
      <motion.div className="presskit-tbd" variants={itemVariants}>
        <span className="tbd-badge">Próximamente</span>
        <p>Información de contacto, tarifas, load-in/load-out y detalles de programación.</p>
      </motion.div>
    </motion.section>
  )
}