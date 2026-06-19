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

export default function Contact() {
  return (
    <section id="contacto" className="fullpage-section">
      <div className="container">
        <motion.div 
          className="section-heading"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          <motion.h2 variants={itemVariants}>Contacto</motion.h2>
          <motion.div className="minimal-line" variants={itemVariants} />
        </motion.div>

        <motion.div 
          className="contact-minimal"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          <motion.p className="impact-phrase" variants={itemVariants}>
            «<strong>Únete</strong> a la ola»
          </motion.p>

          <motion.a 
            href="mailto:septimaolaoficial@gmail.com"
            className="contact-email"
            variants={itemVariants}
          >
            septimaolaoficial@gmail.com
          </motion.a>

          <motion.div 
            className="social-minimal"
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-100px' }}
          >
            <motion.a 
              href="https://instagram.com/septimaolaoficial" 
              target="_blank" 
              rel="noopener noreferrer"
              variants={itemVariants}
              whileHover={{ scale: 1.05 }}
            >
              Instagram
            </motion.a>
            <motion.a 
              href="https://facebook.com/septimaolaoficial" 
              target="_blank" 
              rel="noopener noreferrer"
              variants={itemVariants}
              whileHover={{ scale: 1.05 }}
            >
              Facebook
            </motion.a>
            <motion.a 
              href="https://youtube.com/septimaolaoficial" 
              target="_blank" 
              rel="noopener noreferrer"
              variants={itemVariants}
              whileHover={{ scale: 1.05 }}
            >
              YouTube
            </motion.a>
          </motion.div>

          <motion.p 
            className="contact-location"
            variants={itemVariants}
          >
            Ciudad de México, México
          </motion.p>
        </motion.div>
      </div>
    </section>
  )
}
