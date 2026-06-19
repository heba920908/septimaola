import React, { useState, useEffect } from 'react'
import Hero from './components/Hero'
import News from './components/News'
import Biografia from './components/Biografia'
import Members from './components/Members'
import Discography from './components/Discography'
import Gallery from './components/Gallery'
import Contact from './components/Contact'

export default function App() {
  const [menuOpen, setMenuOpen] = useState(false)

  const toggleMenu = () => {
    setMenuOpen(!menuOpen)
  }

  const closeMenu = () => {
    setMenuOpen(false)
  }

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuOpen && !event.target.closest('.site-header')) {
        closeMenu()
      }
    }

    const handleEscape = (event) => {
      if (event.key === 'Escape' && menuOpen) {
        closeMenu()
      }
    }

    if (menuOpen) {
      document.addEventListener('click', handleClickOutside)
      document.addEventListener('keydown', handleEscape)
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }

    return () => {
      document.removeEventListener('click', handleClickOutside)
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = ''
    }
  }, [menuOpen])

  return (
    <div className="app">
      <header className={`site-header ${menuOpen ? 'menu-open' : ''}`}>
        <div className="header-branding">
          <h1 className="header-title">SÉPTIMA OLA</h1>
          <p className="header-subtitle">Reggae · Ska · Rocksteady</p>
        </div>
        <button 
          className="menu-toggle" 
          onClick={toggleMenu}
          aria-label="Toggle menu"
          aria-expanded={menuOpen}
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
        <nav className={menuOpen ? 'nav-open' : ''}>
          <a href="#inicio" onClick={closeMenu}>Inicio</a>
          <a href="#noticias" onClick={closeMenu}>Noticias</a>
          <a href="#biografia" onClick={closeMenu}>Nosotros</a>
          <a href="#integrantes" onClick={closeMenu}>Banda</a>
          <a href="#musica" onClick={closeMenu}>Música</a>
          <a href="#galeria" onClick={closeMenu}>Galería</a>
          <a href="#contacto" onClick={closeMenu}>Contacto</a>
        </nav>
      </header>

      <main>
        <Hero />
        <News />
        <Biografia />
        <Members />
        <Discography />
        <Gallery />
        <Contact />
      </main>

      <footer className="site-footer">
        <div className="footer-social-links">
          <a
            href="https://instagram.com/septimaolaoficial"
            target="_blank"
            rel="noopener noreferrer"
            className="footer-social-btn"
            aria-label="Instagram"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
              <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>
              <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>
            </svg>
          </a>
          <a
            href="https://facebook.com/septimaolaoficial"
            target="_blank"
            rel="noopener noreferrer"
            className="footer-social-btn"
            aria-label="Facebook"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>
            </svg>
          </a>
          <a
            href="https://youtube.com/septimaolaoficial"
            target="_blank"
            rel="noopener noreferrer"
            className="footer-social-btn"
            aria-label="YouTube"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M2.5 17a24.12 24.12 0 0 1 0-10 2 2 0 0 1 1.4-1.4 49.56 49.56 0 0 1 16.2 0A2 2 0 0 1 21.5 7a24.12 24.12 0 0 1 0 10 2 2 0 0 1-1.4 1.4 49.55 49.55 0 0 1-16.2 0A2 2 0 0 1 2.5 17"/>
              <path d="m10 15 5-3-5-3z"/>
            </svg>
          </a>
        </div>
        <small>© {new Date().getFullYear()} SÉPTIMA OLA — CIUDAD DE MÉXICO</small>
      </footer>
    </div>
  )
}
