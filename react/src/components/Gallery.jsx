import React, { useState, useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'
import useEmblaCarousel from 'embla-carousel-react'

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
  const [emblaRef, emblaApi] = useEmblaCarousel({
    dragFree: false,
    align: 'center',
    loop: false,
  })
  const [selectedIndex, setSelectedIndex] = useState(0)

  const onSelect = useCallback(() => {
    if (!emblaApi) return
    setSelectedIndex(emblaApi.selectedScrollSnap())
  }, [emblaApi])

  useEffect(() => {
    if (!emblaApi) return
    onSelect()
    emblaApi.on('select', onSelect)
    return () => {
      emblaApi.off('select', onSelect)
    }
  }, [emblaApi, onSelect])

  const scrollTo = useCallback(
    (index) => emblaApi && emblaApi.scrollTo(index),
    [emblaApi]
  )

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

        {/* Desktop Grid View */}
        <motion.div
          className="gallery-desktop"
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
                loading="lazy"
                decoding="async"
                onError={(e) => { e.currentTarget.style.display = 'none' }}
              />
            </motion.div>
          ))}
        </motion.div>

        {/* Mobile Carousel View */}
        <div className="gallery-carousel">
          <div className="gallery-carousel-viewport" ref={emblaRef}>
            <div className="gallery-carousel-container">
              {galleryImages.map((img, idx) => (
                <div key={idx} className="gallery-carousel-slide">
                  <img
                    src={`${import.meta.env.BASE_URL}images/gallery/${img.slug}.jpg`}
                    alt={img.alt}
                    loading={idx === 0 ? 'eager' : 'lazy'}
                    decoding="async"
                    onError={(e) => { e.currentTarget.style.display = 'none' }}
                  />
                </div>
              ))}
            </div>
          </div>
          <div className="gallery-carousel-dots">
            {galleryImages.map((_, idx) => (
              <button
                key={idx}
                className={`gallery-carousel-dot ${idx === selectedIndex ? 'active' : ''}`}
                onClick={() => scrollTo(idx)}
                aria-label={`Ir a foto ${idx + 1}`}
              />
            ))}
          </div>
        </div>

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
