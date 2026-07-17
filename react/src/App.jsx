import React, { useState, useEffect, useRef, useCallback } from 'react'
import Hero from './components/Hero'
import News from './components/News'
import Biografia from './components/Biografia'
import Members from './components/Members'
import Discography from './components/Discography'
import Gallery from './components/Gallery'
import Contact from './components/Contact'
import PressKit from './components/presskit/PressKit'
import PrivacyNotice from './components/privacy/PrivacyNotice'

export default function App() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [currentRoute, setCurrentRoute] = useState('')
  const navRef = useRef(null)
  const menuToggleRef = useRef(null)
  const lastFocusedElement = useRef(null)

  const toggleMenu = () => {
    setMenuOpen(!menuOpen)
  }

  const closeMenu = () => {
    setMenuOpen(false)
  }

  // Focus trap for mobile nav drawer
  const trapFocus = useCallback((element) => {
    const focusableElements = element.querySelectorAll(
      'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select'
    )
    const firstFocusable = focusableElements[0]
    const lastFocusable = focusableElements[focusableElements.length - 1]

    const handleTabKey = (e) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstFocusable) {
            lastFocusable.focus()
            e.preventDefault()
          }
        } else {
          if (document.activeElement === lastFocusable) {
            firstFocusable.focus()
            e.preventDefault()
          }
        }
      }
    }

    element.addEventListener('keydown', handleTabKey)
    return () => element.removeEventListener('keydown', handleTabKey)
  }, [])

  // Swipe to dismiss nav drawer
  const touchStartX = useRef(0)
  const touchEndX = useRef(0)

  const handleTouchStart = (e) => {
    touchStartX.current = e.changedTouches[0].screenX
  }

  const handleTouchEnd = (e) => {
    touchEndX.current = e.changedTouches[0].screenX
    handleSwipe()
  }

  const handleSwipe = () => {
    const swipeThreshold = 50
    const diff = touchStartX.current - touchEndX.current
    // Swipe right to open (from right edge), swipe left to close
    if (diff > swipeThreshold && menuOpen) {
      // Swiped left - close menu
      closeMenu()
    }
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

    // Hash change handler for routing
    const handleHashChange = () => {
      const hash = window.location.hash
      if (hash.startsWith('#/')) {
        setCurrentRoute(hash.substring(2))
      } else {
        setCurrentRoute('')
      }
    }

    // Initialize route on first load
    handleHashChange()

    if (menuOpen) {
      // Save current focus
      lastFocusedElement.current = document.activeElement
      document.addEventListener('click', handleClickOutside)
      document.addEventListener('keydown', handleEscape)
      document.body.style.overflow = 'hidden'
      // Focus first nav item
      setTimeout(() => {
        if (navRef.current) {
          const firstLink = navRef.current.querySelector('a')
          if (firstLink) firstLink.focus()
          trapFocus(navRef.current)
        }
      }, 100)
    } else {
      document.body.style.overflow = ''
      // Return focus to toggle button
      if (menuToggleRef.current) {
        menuToggleRef.current.focus()
      }
    }

    // Add event listeners
    window.addEventListener('hashchange', handleHashChange)
    document.addEventListener('click', handleClickOutside)
    document.addEventListener('keydown', handleEscape)

    return () => {
      window.removeEventListener('hashchange', handleHashChange)
      document.removeEventListener('click', handleClickOutside)
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = ''
    }
  }, [menuOpen, trapFocus])

  return (
    <div className="app">
      <header className={`site-header ${menuOpen ? 'menu-open' : ''}`}>
        <div className="header-branding">
          <h1 className="header-title">SÉPTIMA OLA</h1>
          <p className="header-subtitle">Reggae · Ska · Rocksteady</p>
        </div>
        <button
          ref={menuToggleRef}
          className="menu-toggle"
          onClick={toggleMenu}
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
          aria-label={menuOpen ? 'Cerrar menú' : 'Abrir menú'}
          aria-expanded={menuOpen}
          aria-controls="main-nav"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
        <nav
          ref={navRef}
          id="main-nav"
          className={menuOpen ? 'nav-open' : ''}
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
        >
          <a href="#inicio" onClick={closeMenu}>Inicio</a>
          <a href="#contacto" onClick={closeMenu}>Contacto</a>
          <a href="#noticias" onClick={closeMenu}>Noticias</a>
          <a href="#musica" onClick={closeMenu}>Música</a>
          <a href="#integrantes" onClick={closeMenu}>Banda</a>
          <a href="#galeria" onClick={closeMenu}>Galería</a>
        </nav>
      </header>

      <main>
        {currentRoute === 'press-kit' ? (
          <PressKit />
        ) : currentRoute === 'privacy-notice' ? (
          <PrivacyNotice />
        ) : (
          <>
            <Hero />
            <Contact />
            <News />
            <Discography />
            <Members />
            <Gallery />
            <Biografia />
          </>
        )}
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
        <a href="#/press-kit" className="footer-presskit-link">Press &amp; Production Kit</a>
        <a href="#/privacy-notice" className="footer-legal-link">Aviso de Privacidad</a>
        <small>© {new Date().getFullYear()} SÉPTIMA OLA — CIUDAD DE MÉXICO</small>
      </footer>
    </div>
  )
}
