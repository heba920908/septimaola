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
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: [0.16, 1, 0.3, 1],
    },
  },
}

const galleryImages = [
  { slug: 'photo-1', alt: 'Séptima Ola — Foto oficial 1' },
  { slug: 'photo-2', alt: 'Séptima Ola — Foto oficial 2' },
]

export default function Gallery() {
  return (
    <section id="galeria" className="fullpage-section">
      <div className="container">
        <motion.div
          className="section-heading"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          <motion.h2 variants={itemVariants}>Galería</motion.h2>
          <motion.div className="minimal-line" variants={itemVariants} />
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          <motion.p className="impact-phrase" variants={itemVariants}>
            «<strong>Imágenes</strong> que hablan más que mil canciones»
          </motion.p>
        </motion.div>

        <motion.div
          className="gallery-minimal"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          {galleryImages.map((img, idx) => (
            <motion.div
              key={idx}
              variants={itemVariants}
              whileHover={{ scale: 1.02, opacity: 1 }}
            >
              <img
                src={`${import.meta.env.BASE_URL}images/gallery/${img.slug}.jpg`}
                alt={img.alt}
                onError={(e) => { e.currentTarget.style.display = 'none' }}
                style={{
                  width: '100%',
                  height: '200px',
                  objectFit: 'cover',
                  borderRadius: '8px',
                  display: 'block',
                }}
              />
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
          Fotos oficiales de alta resolución disponibles bajo petición.
        </motion.p>
      </div>
    </section>
  )
}
