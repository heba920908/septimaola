import React from 'react'
import { motion } from 'framer-motion'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
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

const songs = [
  { title: 'Desde mi Ventana', url: 'https://hypeddit.com/qyhyl7' },
  { title: 'Despertar', url: 'https://open.spotify.com/search?q=Septima+Ola' },
  { title: 'Arenga', url: 'https://open.spotify.com/search?q=Septima+Ola' },
  { title: 'A Contraluz', url: 'https://open.spotify.com/search?q=Septima+Ola' },
  { title: 'Acelera', url: 'https://open.spotify.com/search?q=Septima+Ola' },
]

export default function Discography() {
  return (
    <section id="musica" className="fullpage-section">
      <div className="container">
        <motion.div
          className="section-heading"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          <motion.h2 variants={itemVariants}>Música</motion.h2>
          <motion.div className="minimal-line" variants={itemVariants} />
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          <motion.p className="impact-phrase" variants={itemVariants}>
            «<strong>Sonidos que despiertan</strong>. Una propuesta para la escena actual.»
          </motion.p>
        </motion.div>

        <motion.div
          className="discography-minimal"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          {songs.map((song, idx) => (
            <motion.div
              key={idx}
              className="song-minimal"
              variants={itemVariants}
              whileHover={{ x: 8 }}
              whileTap={{ scale: 0.99 }}
            >
              <h3>{song.title}</h3>
              <a
                href={song.url}
                target="_blank"
                rel="noopener noreferrer"
                className="play-btn"
                aria-label={`Escuchar ${song.title}`}
              >
                ▶
              </a>
            </motion.div>
          ))}
        </motion.div>

        <motion.p
          className="minimal-text"
          variants={itemVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          Masters disponibles para prensa y promociones.
        </motion.p>
      </div>
    </section>
  )
}
