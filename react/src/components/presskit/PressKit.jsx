import React from 'react'
import { motion } from 'framer-motion'
import TechnicalRider from './TechnicalRider'
import HospitalityRider from './HospitalityRider'
import BookingLogistics from './BookingLogistics'
import Downloads from './Downloads'

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

export default function PressKit() {
  const handleBackClick = (e) => {
    e.preventDefault()
    window.location.hash = ''
  }

  return (
    <div className="presskit-page">
      <div className="presskit-header">
        <div className="container">
          <motion.div
            className="back-link-container"
            variants={itemVariants}
          >
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
            <motion.h1 variants={itemVariants}>Kit de Prensa y Producción</motion.h1>
            <motion.div className="minimal-line" variants={itemVariants} />
          </motion.div>
          
          <motion.p className="impact-phrase" variants={itemVariants}>
            Información profesional para medios, producción y bookers
          </motion.p>
        </div>
      </div>

      <div className="container">
        <motion.div
          className="presskit-navigation"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.a href="#technical-rider" variants={itemVariants} className="nav-link">
            Rider Técnico
          </motion.a>
          <motion.a href="#hospitality-rider" variants={itemVariants} className="nav-link">
            Rider de Hospitalidad
          </motion.a>
          <motion.a href="#booking-logistics" variants={itemVariants} className="nav-link">
            Reservas y Logística
          </motion.a>
          <motion.a href="#downloads" variants={itemVariants} className="nav-link">
            Descargas
          </motion.a>
        </motion.div>

        <TechnicalRider />
        <HospitalityRider />
        <BookingLogistics />
        <Downloads />
      </div>
    </div>
  )
}