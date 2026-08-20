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
    { name: 'Arthur', role: 'Bajo eléctrico / stage manager' },
    { name: 'Gil', role: 'Batería' },
    { name: 'Levi\'Sax', role: 'Sax tenor' },
    { name: 'Rodrigo Mera', role: 'Violinista y Arreglista' },
    { name: 'Sandy Robinsuell', role: 'Tecladista y vocalista corista' },
    { name: 'Itzel Calzada', role: 'Ingeniera de sonido' },
    { name: 'Mirna Mera', role: 'Fotógrafa' },
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
      <motion.h3 variants={itemVariants}>Crew list / Equipo de trabajo</motion.h3>
      
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
                <td data-label="Nombre">{member.name}</td>
                <td data-label="Rol">{member.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </motion.div>
    </motion.div>
  )
}