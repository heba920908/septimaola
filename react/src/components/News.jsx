import React, { useState, useEffect, useRef } from 'react'
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

const FB_PAGE_URL = 'https://www.facebook.com/septimaolaoficial'
const FB_PAGE_PLUGIN_SRC = `https://www.facebook.com/plugins/page.php?href=${encodeURIComponent(FB_PAGE_URL)}&tabs=timeline&small_header=true&adapt_container_width=true&hide_cover=true&show_facepile=false&width=500&height=500`

export default function News() {
  const [isVisible, setIsVisible] = useState(false)
  const sectionRef = useRef(null)

  useEffect(() => {
    // IntersectionObserver to defer iframe loading
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.disconnect()
        }
      },
      {
        rootMargin: '100px',
        threshold: 0.1,
      }
    )

    if (sectionRef.current) {
      observer.observe(sectionRef.current)
    }

    return () => {
      if (sectionRef.current) {
        observer.unobserve(sectionRef.current)
      }
    }
  }, [])

  return (
    <section id="noticias" className="fullpage-section" ref={sectionRef}>
      <div className="container">
        <motion.div
          className="section-heading"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          <motion.h2 variants={itemVariants}>Noticias</motion.h2>
          <motion.div className="minimal-line" variants={itemVariants} />
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          <motion.p className="impact-phrase" variants={itemVariants}>
            «Cada concierto es una <strong>ola nueva</strong>»
          </motion.p>
        </motion.div>

        <motion.div
          className="news-minimal"
          variants={itemVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          {isVisible ? (
            <iframe
              title="Noticias de Facebook"
              src={FB_PAGE_PLUGIN_SRC}
              loading="lazy"
              scrolling="no"
              frameBorder="0"
              allowFullScreen
              allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"
            />
          ) : (
            <div className="news-minimal-placeholder">
              <p>Cargando noticias...</p>
            </div>
          )}
        </motion.div>
      </div>
    </section>
  )
}
