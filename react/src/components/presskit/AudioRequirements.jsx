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

export default function AudioRequirements() {
  const requirements = [
    'El espectáculo requiere una posición completa de mezcla Front of House (FOH) y un área independiente de monitoreo en el escenario.',
    'El FOH debe colocarse aproximadamente a 20 m del frente del escenario y a unos 1 m de altura para una mezcla precisa de referencia de audiencia.',
    'El sistema PA debe ser de grado profesional. No hay marca específica obligatoria, pero se recomiendan Electro-Voice, Bose o JBL.',
    'El monitoreo en el escenario debe incluir capacidad anti-retroalimentación.',
    'Consola de mezcla: mínimo 8 canales de entrada (banda de 6 miembros), con suficientes buses auxiliares para las mezclas de monitores.',
    'La salida del sistema debe alcanzar al menos 100 dB SPL.',
    'La guitarra y el bajo requieren cajas directas (DI) o amplificadores de monitor.',
    'El violín y el saxofón requieren cajas directas (DI).',
    'El canal del saxofón debe incluir compresión.'
  ]

  return (
    <motion.div
      id="audio"
      className="presskit-subsection"
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-100px' }}
    >
      <motion.h3 variants={itemVariants}>Requisitos de Audio</motion.h3>
      
      <motion.ul className="presskit-list" variants={itemVariants}>
        {requirements.map((requirement, index) => (
          <li key={index}>{requirement}</li>
        ))}
      </motion.ul>
    </motion.div>
  )
}