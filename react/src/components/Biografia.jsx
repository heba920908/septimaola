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

export default function Biografia() {
  return (
    <section id="biografia" className="fullpage-section">
      <div className="container container-narrow">
        <motion.div 
          className="section-heading"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          <motion.h2 variants={itemVariants}>Nosotros</motion.h2>
          <motion.div className="minimal-line" variants={itemVariants} />
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          <motion.p className="impact-phrase" variants={itemVariants}>
            «Donde el <strong>reggae jamaicano</strong> encuentra el <strong>corazón latino</strong>»
          </motion.p>

          <motion.p className="minimal-text" variants={itemVariants}>
            Nacidos en Ciudad de México, fusionamos reggae, ska y rocksteady con la pasión de nuestra tierra. 
            Cada canción es un puente entre culturas, un grito de libertad, una celebración de la vida.
          </motion.p>
        </motion.div>

        <motion.div 
          className="vision-mission-minimal"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          <motion.div className="vision-card" variants={itemVariants}>
            <h3>Visión</h3>
            <p>Ser la voz reggae más auténtica de México, llevando mensajes de paz y justicia social a escenarios globales.</p>
          </motion.div>
          <motion.div className="mission-card" variants={itemVariants}>
            <h3>Misión</h3>
            <p>Crear música que conecte el alma mexicana con el espíritu universal del reggae.</p>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}
