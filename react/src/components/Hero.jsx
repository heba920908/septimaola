import React from 'react'
import { motion } from 'framer-motion'
import logo from '../assets/logo.png'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
      delayChildren: 0.3,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 40 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.8,
      ease: [0.16, 1, 0.3, 1],
    },
  },
}

const logoVariants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 1,
      ease: [0.16, 1, 0.3, 1],
    },
  },
}

export default function Hero() {
  return (
    <section id="inicio" className="fullpage-section hero">
      <motion.div
        className="hero-content"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.img
          src={logo}
          alt="SÉPTIMA OLA"
          className="hero-logo"
          variants={logoVariants}
        />
        <motion.h1 variants={itemVariants}>
          SÉPTIMA OLA
        </motion.h1>
        <motion.div className="minimal-line" variants={itemVariants} />
        <motion.p className="tagline" variants={itemVariants}>
          El sonido de tod@s
        </motion.p>
        <motion.p className="lead" variants={itemVariants}>
          Reggae · Ska · Rocksteady desde las raíces hasta el horizonte
        </motion.p>

        <motion.a
          className="presskit-btn"
          href="https://drive.google.com/file/d/1bV4JgTpkhVVMLHrzG9m4ke5q4n1Ts8hE/view?usp=sharing"
          target="_blank"
          rel="noopener noreferrer"
          variants={itemVariants}
          whileHover={{ y: -3, boxShadow: '0 8px 30px rgba(0,212,255,0.4)' }}
          whileTap={{ scale: 0.98 }}
        >
          Press Kit
        </motion.a>

        <motion.div
          className="hero-social-links"
          variants={itemVariants}
        >
          <a
            href="https://instagram.com/septimaolaoficial"
            target="_blank"
            rel="noopener noreferrer"
            className="hero-social-btn"
            aria-label="Instagram"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
              <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>
              <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>
            </svg>
          </a>
          <a
            href="https://facebook.com/septimaolaoficial"
            target="_blank"
            rel="noopener noreferrer"
            className="hero-social-btn"
            aria-label="Facebook"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>
            </svg>
          </a>
          <a
            href="https://youtube.com/septimaolaoficial"
            target="_blank"
            rel="noopener noreferrer"
            className="hero-social-btn"
            aria-label="YouTube"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M2.5 17a24.12 24.12 0 0 1 0-10 2 2 0 0 1 1.4-1.4 49.56 49.56 0 0 1 16.2 0A2 2 0 0 1 21.5 7a24.12 24.12 0 0 1 0 10 2 2 0 0 1-1.4 1.4 49.55 49.55 0 0 1-16.2 0A2 2 0 0 1 2.5 17"/>
              <path d="m10 15 5-3-5-3z"/>
            </svg>
          </a>
        </motion.div>
      </motion.div>

      <motion.div 
        className="scroll-indicator"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2, duration: 1 }}
      >
        Desliza
      </motion.div>
    </section>
  )
}
