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

export default function CrewList() {
  const crewMembers = [
    { name: 'Alfred Herrera', role: 'Guitarra / stage manager' },
    { name: 'Arthur', role: 'Bajo electrico / stage manager' },
    { name: 'Levi\'Sax', role: 'Sax tenor / stage manager' },
    { name: 'Rodrigo Mera', role: 'Violinista y Arreglista / stage manager' },
    { name: 'Sandy Robinsuell', role: 'Vocalista / stage manager' },
    { name: 'lemanu', role: 'Batería / stage manager' }
  ]

  return (
    <motion.div
      id="crew"
      className="presskit-subsection"
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-100px' }}
    >
      <motion.h3 variants={itemVariants}>Lista de Personal</motion.h3>
      
      <motion.div className="crew-table-container" variants={itemVariants}>
        <table className="presskit-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Rol</th>
            </tr>
          </thead>
          <tbody>
            {crewMembers.map((member, index) => (
              <tr key={index}>
                <td>{member.name}</td>
                <td>{member.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </motion.div>
    </motion.div>
  )
}