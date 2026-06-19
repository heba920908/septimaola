import React from 'react'
import { motion } from 'framer-motion'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.2,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.16, 1, 0.3, 1],
    },
  },
}

const members = [
  { name: 'Alfred YearckLei', role: 'Guitarra · Voz', image: 'alfred', imagePosition: 'top' },
  { name: 'lemanu', role: 'Batería', image: 'lemanu', imagePosition: 'top' },
  { name: 'Levi\'Sax', role: 'Saxofón', image: 'levisax', imagePosition: 'top' },
  { name: 'Rodrigo Mera', role: 'Violín', image: 'rodrigo', imagePosition: 'top' },
  { name: 'Sandy Robinsuell', role: 'Teclado · Voz', image: 'sandy', imagePosition: 'center' },
  { name: 'Arthur', role: 'Bajo', image: 'arthur', imagePosition: 'center' },
]

export default function Members() {
  return (
    <section id="integrantes" className="fullpage-section">
      <div className="container">
        <motion.div
          className="section-heading"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          <motion.h2 variants={itemVariants}>La Banda</motion.h2>
          <motion.div className="minimal-line" variants={itemVariants} />
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          <motion.p className="impact-phrase" variants={itemVariants}>
            «<strong>Seis almas</strong>, un solo latido»
          </motion.p>
        </motion.div>

        <motion.div
          className="members-minimal"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          {members.map((member, idx) => (
            <motion.div
              key={idx}
              className="member-minimal"
              variants={itemVariants}
              whileHover={{ y: -5 }}
            >
              <div className="member-image-wrap">
                <img
                  src={`${import.meta.env.BASE_URL}images/members/${member.image}.jpg`}
                  alt={member.name}
                  onError={(e) => { e.currentTarget.style.display = 'none' }}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                    objectPosition: member.imagePosition || 'center',
                  }}
                />
              </div>
              <h3>{member.name}</h3>
              <p className="role">{member.role}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
