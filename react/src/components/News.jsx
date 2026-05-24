import React, { useState, useEffect, useRef } from 'react'
import Section from './Section'

const NEWS_ITEMS = [
  {
    id: 1,
    type: 'Concierto',
    title: 'Foro Indie Rocks — Ciudad de México',
    date: '14 de junio, 2026',
    description:
      'Séptima Ola se presentará en el Foro Indie Rocks con su set completo de reggae, ska y rocksteady. Puertas abren a las 20:00 h. Entrada libre.',
    link: 'https://www.instagram.com/septimaolareg/',
    linkLabel: 'Más info',
  },
  {
    id: 2,
    type: 'Grabación',
    title: 'Nuevo sencillo en producción',
    date: 'Mayo 2026',
    description:
      'Estamos en el estudio grabando nuestro próximo sencillo. Pronto anunciaremos fecha de lanzamiento y colaboradores. ¡Mantente al pendiente en nuestras redes!',
    link: null,
    linkLabel: null,
  },
  {
    id: 3,
    type: 'Prensa',
    title: '"El reggae mexicano tiene nueva voz" — Chilango',
    date: 'Abril 2026',
    description:
      'La revista Chilango nos dedicó una reseña tras nuestra presentación en el Festival de las Culturas Amigas. "Una banda que sabe bailar entre raíces jamaicanas y corazón chilango."',
    link: 'https://www.instagram.com/septimaolareg/',
    linkLabel: 'Leer nota',
  },
]

const INTERVAL_MS = 5000

export default function News() {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [paused, setPaused] = useState(false)
  const timerRef = useRef(null)

  const next = () => setCurrentIndex(i => (i + 1) % NEWS_ITEMS.length)
  const prev = () => setCurrentIndex(i => (i + NEWS_ITEMS.length - 1) % NEWS_ITEMS.length)
  const goTo = (index) => setCurrentIndex(index)

  useEffect(() => {
    if (paused) return
    timerRef.current = setInterval(next, INTERVAL_MS)
    return () => clearInterval(timerRef.current)
  }, [paused, currentIndex])

  const item = NEWS_ITEMS[currentIndex]

  return (
    <Section id="noticias" title="Noticias">
      <div
        className="news-slider"
        onMouseEnter={() => setPaused(true)}
        onMouseLeave={() => setPaused(false)}
      >
        <div className="news-card" key={item.id}>
          <span className="news-badge">{item.type}</span>
          <p className="news-date">{item.date}</p>
          <h3>{item.title}</h3>
          <p className="news-description">{item.description}</p>
          {item.link && (
            <a
              href={item.link}
              className="btn-primary news-link"
              target="_blank"
              rel="noopener noreferrer"
            >
              {item.linkLabel}
            </a>
          )}
        </div>

        <div className="news-nav-row">
          <button className="news-btn" onClick={prev} aria-label="Anterior">&#8592;</button>
          <div className="news-dots" role="tablist" aria-label="Noticias">
            {NEWS_ITEMS.map((n, i) => (
              <button
                key={n.id}
                className={`news-dot${i === currentIndex ? ' active' : ''}`}
                onClick={() => goTo(i)}
                aria-label={`Noticia ${i + 1}`}
                role="tab"
                aria-selected={i === currentIndex}
              />
            ))}
          </div>
          <button className="news-btn" onClick={next} aria-label="Siguiente">&#8594;</button>
        </div>
      </div>
    </Section>
  )
}
