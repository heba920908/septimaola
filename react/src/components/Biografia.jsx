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
            «En una era donde el mundo parece más dividido que nunca <strong>Séptima Ola</strong> emerge como una <strong>respuesta</strong>»
          </motion.p>

          <motion.p className="minimal-text" variants={itemVariants}>
            Séptima Ola combina reggae, ska y rocksteady para crear un sonido distintivo con melodías
            pegajosas, ritmos bailables y letras conscientes enfocadas en el amor, la unidad y la
            justicia social.
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
            <h3>Nuestro Norte</h3>
            <p>Sonidos hechos en México para corazones inquietos que buscan movimiento e inspiración.</p>
          </motion.div>
          <motion.div className="mission-card" variants={itemVariants}>
            <h3>Se parte de la ola</h3>
            <p> Ven, súbete a la ola nacida de nuestra tierra y que se expande sin
            límites en una fusión de ritmos.</p>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}
