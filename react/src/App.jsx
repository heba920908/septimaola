import React, { useState, useEffect } from 'react'
import Hero from './components/Hero'
import Section from './components/Section'
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

  // Close menu when clicking outside or on escape key
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
      // Prevent body scroll when menu is open
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
          <a href="#biografia" onClick={closeMenu}>Biografía</a>
          <a href="#integrantes" onClick={closeMenu}>Integrantes</a>
          <a href="#musica" onClick={closeMenu}>Música</a>
          <a href="#galeria" onClick={closeMenu}>Galería</a>
          <a href="#contacto" onClick={closeMenu}>Contacto</a>
        </nav>
      </header>

      <Hero />

      <main>
        <Section id="biografia" title="¿Quiénes somos?">
          <p>
            Séptima Ola emerge desde las calles vibrantes de Ciudad de México como una ola imparable de fusión musical, donde el reggae jamaicano se encuentra con el corazón latino, el ska británico con el alma mexicana, y el rocksteady con la pasión de nuestra gente. Nacidos en la tierra del mariachi y la cumbia, pero enamorados de las raíces rasta, somos la prueba viva de que la música no conoce fronteras.
          </p>
          <p>
            En nuestro departamento en La Raza, donde Alfred Herrera comenzó a tejer los primeros acordes de esta aventura sonora, hemos creado un espacio donde la diversidad es nuestra mayor fortaleza. Nuestros integrantes traen consigo historias únicas: desde el saxofón de Levi, que ha conquistado escenarios desde Texcoco hasta el Centro Cultural México Bicentenario, pasando por el violín clásico de Rodrigo Mera que se reinventa en ritmos festivos, hasta la percusión contagiosa de Ingri Mona que fusiona salsa y reggae con maestría innata.
          </p>
          <p>
            Somos la banda que hace bailar a los amantes del reggae en México, que lleva la conciencia social a las plazas públicas, que transforma el dolor colectivo en canciones de esperanza. Nuestras letras hablan de amor en tiempos de crisis, de unidad en una ciudad dividida, de justicia social mientras el mundo cambia. Cada riff de guitarra de Alfred, cada golpe de batería de Lemánu, cada nota de bajo de Arthur, cada voz de Sandy Robinsuell, nos recuerda que la música es el puente entre culturas, el grito de libertad, la celebración de la vida.
          </p>
          <p>
            En una época donde el mundo parece más dividido que nunca, Séptima Ola surge como respuesta: reggae hecho en México, para mexicanos y para el mundo. Invitamos a todos los corazones inquietos, a los que buscan ritmo en el caos urbano, a los que creen que una canción puede cambiar el mundo. Únete a nuestra ola, siente el poder de la música que nace de las raíces profundas de nuestra tierra, pero que se eleva hacia horizontes infinitos.
          </p>
          <div className="vision-mission">
            <div className="vision">
              <h3>Visión</h3>
              <p>Ser la voz reggae más auténtica de México, reconocida internacionalmente por fusionar las tradiciones musicales mexicanas con las raíces jamaicanas, llevando mensajes de paz, amor y justicia social a través de escenarios que van desde las cantinas tradicionales hasta los grandes festivales globales.</p>
            </div>
            <div className="mission">
              <h3>Misión</h3>
              <p>Crear música que conecte el alma mexicana con el espíritu universal del reggae, fomentando comunidad, empoderamiento y transformación social. Cada canción es una invitación a bailar, reflexionar y soñar con un mundo mejor, donde la diversidad cultural sea nuestra mayor riqueza y la música nuestro idioma común.</p>
            </div>
          </div>
        </Section>

        <Members />

        <Discography />

        <Gallery />

        <Contact />
      </main>

      <footer className="site-footer">
        <small>© {new Date().getFullYear()} SÉPTIMA OLA — Ciudad de México</small>
      </footer>
    </div>
  )
}
