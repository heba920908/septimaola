import React from 'react'
import { motion } from 'framer-motion'

const sectionVariants = {
  hidden: { opacity: 0, y: 40 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      ease: [0.16, 1, 0.3, 1],
    },
  },
}

export default function Section({ id, title, children }) {
  return (
    <motion.section
      id={id}
      className="section"
      variants={sectionVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-100px' }}
    >
      <div className="container">
        <h2>{title}</h2>
        <div>{children}</div>
      </div>
    </motion.section>
  )
}
