import React, { useState, useEffect } from 'react'
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

// Web Share API fallback component
function ShareButton() {
  const [canShare, setCanShare] = useState(false)

  useEffect(() => {
    setCanShare(typeof navigator !== 'undefined' && !!navigator.share)
  }, [])

  const handleShare = async () => {
    // Haptic feedback on Android
    if (navigator.vibrate) {
      navigator.vibrate(8)
    }

    if (canShare) {
      try {
        await navigator.share({
          title: 'SÉPTIMA OLA - Reggae · Ska · Rocksteady',
          text: 'Conoce a Séptima Ola, banda de reggae/ska de Ciudad de México',
          url: window.location.href,
        })
      } catch (err) {
        // User cancelled or share failed - fallback to opening press kit
        window.open(
          'https://drive.google.com/file/d/1o_ODH3OizxgFXNNM5PLdVOC0Ww4r7hEf/view?usp=drivesdk',
          '_blank',
          'noopener,noreferrer'
        )
      }
    } else {
      // Fallback for browsers without Web Share API
      window.open(
        'https://drive.google.com/file/d/1o_ODH3OizxgFXNNM5PLdVOC0Ww4r7hEf/view?usp=drivesdk',
        '_blank',
        'noopener,noreferrer'
      )
    }
  }

  return (
    <motion.button
      className="presskit-btn"
      onClick={handleShare}
      variants={itemVariants}
      whileTap={{ scale: 0.98 }}
    >
      {canShare ? 'Compartir' : 'Press Kit'}
    </motion.button>
  )
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
          fetchpriority="high"
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

        <ShareButton />

        {/* Mobile CTA row - tel and mailto */}
        <motion.div
          className="hero-cta-row"
          variants={itemVariants}
        >
          <a
            href="tel:+525555555555"
            className="hero-cta-btn"
            aria-label="Llamar"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
            </svg>
          </a>
          <a
            href="mailto:septimaolaoficial@gmail.com"
            className="hero-cta-btn"
            aria-label="Enviar correo"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
              <polyline points="22,6 12,13 2,6"/>
            </svg>
          </a>
        </motion.div>

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
