import React from 'react'
import { motion } from 'framer-motion'
import CrewList from './CrewList'
import AudioRequirements from './AudioRequirements'
import InputList from './InputList'
import StagePlot from './StagePlot'

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

export default function TechnicalRider() {
  return (
    <motion.section
      id="technical-rider"
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
        <motion.h2 variants={itemVariants}>Rider Técnico</motion.h2>
        <motion.div className="minimal-line" variants={itemVariants} />
      </motion.div>

      <CrewList />
      <AudioRequirements />
      <InputList />
      <StagePlot />
    </motion.section>
  )
}