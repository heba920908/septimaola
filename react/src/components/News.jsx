import React, { useState, useEffect, useRef } from 'react'
import Section from './Section'

const ALLOWED_EMBED_ORIGINS = [
  'https://www.facebook.com/plugins/',
  'https://www.instagram.com/p/',
  'https://www.instagram.com/reel/',
]

function isAllowedEmbed(src) {
  return ALLOWED_EMBED_ORIGINS.some(origin => src.startsWith(origin))
}

const NEWS_ITEMS = [
  {
    id: 1,
    type: 'Lanzamiento',
    title: 'Desde mi ventana — Nuevo sencillo',
    date: '30 de mayo, 2026',
    description:
      'Séptima Ola se presentará su nuevo sencillo "Desde mi ventana". Puertas abren a las 20:00 h. Entrada libre.',
    embed: 'https://www.facebook.com/plugins/post.php?href=https%3A%2F%2Fwww.facebook.com%2Fseptimaolaoficial%2Fposts%2Fpfbid0v5yAqWmx4a9v9YCcbmGu6Ds5sv4givdwg2NbEf94YMPMeeMBtZ87cSohdbWipSpnl&show_text=true&width=500',
    image: null,
    link: 'https://www.facebook.com/septimaolaoficial',
    linkLabel: 'Ver en Facebook',
  },
  {
    id: 2,
    type: 'Entrevista',
    title: 'Entrevista y acústico — Prensa Fan Oficial',
    date: 'Mayo 2026',
    description:
      'Estábamos en entrevista con Prensa Fan Oficial y acabamos en un acústico!! Dale play ▶️🌊',
    embed: 'https://www.facebook.com/plugins/post.php?href=https%3A%2F%2Fwww.facebook.com%2Fseptimaolaoficial%2Fposts%2Fpfbid02YFnZ8ZUm7QtCyNbw8X229s9525Rxzxv985H6Yh8RQzCgnDCX396fyLKBFPjqqcT8l&show_text=true&width=500',
    image: null,
    link: 'https://www.facebook.com/septimaolaoficial',
    linkLabel: 'Ver en Facebook',
  },
  {
    id: 3,
    type: 'Prensa',
    title: '"El reggae mexicano tiene nueva voz" — Chilango',
    date: 'Abril 2026',
    description:
      'La revista Chilango nos dedicó una reseña tras nuestra presentación en el Festival de las Culturas Amigas. "Una banda que sabe bailar entre raíces jamaicanas y corazón chilango."',
    embed: 'https://www.instagram.com/reel/DYgTnsgMoNt/embed/',
    image: null,
    link: 'https://www.instagram.com/reel/DYgTnsgMoNt/',
    linkLabel: 'Ver en Instagram',
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
        <div className={`news-card${(item.image || item.embed) ? ' news-card--has-media' : ''}`} key={item.id}>
          {item.embed && isAllowedEmbed(item.embed) && (
            <div className="news-embed">
              <iframe
                src={item.embed}
                title={item.title}
                scrolling="no"
                frameBorder="0"
                allowFullScreen
                allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"
              />
            </div>
          )}
          {!item.embed && item.image && (
            <div className="news-preview">
              <img
                src={item.image}
                alt={item.title}
                className="news-preview-img"
                onError={(e) => { e.target.parentElement.style.display = 'none' }}
              />
            </div>
          )}
          <div className="news-body">
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
