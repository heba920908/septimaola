import React from 'react'
import Hero from './components/Hero'
import Section from './components/Section'
import Members from './components/Members'
import Discography from './components/Discography'
import Gallery from './components/Gallery'
import Contact from './components/Contact'

export default function App() {
  return (
    <div className="app">
      <header className="site-header">
        <div className="header-branding">
          <h1 className="header-title">SÉPTIMA OLA</h1>
          <p className="header-subtitle">Reggae · Ska · Rocksteady</p>
        </div>
        <nav>
          <a href="#biografia">Biografía</a>
          <a href="#integrantes">Integrantes</a>
          <a href="#musica">Música</a>
          <a href="#galeria">Galería</a>
          <a href="#contacto">Contacto</a>
        </nav>
      </header>

      <Hero />

      <main>
        <Section id="biografia" title="¿Quiénes somos?">
          <p>
            Séptima Ola nace en Ciudad de México como una fusión honesta entre reggae, ska y rocksteady, con letras orientadas a la unión y la conciencia social.
          </p>
          <p>
            Una banda que fusiona ritmos latinos con melodías contemporáneas para crear una experiencia sonora única. Nuestra música celebra la diversidad cultural y la pasión por la innovación, invitando a todos a sumergirse en un viaje de sonidos vibrantes y emociones auténticas.
          </p>
          <div className="vision-mission">
            <div className="vision">
              <h3>Visión</h3>
              <p>Ser una fuerza líder en la escena del reggae y ska, conocida por nuestro sonido auténtico, letras significativas y compromiso con la integridad artística.</p>
            </div>
            <div className="mission">
              <h3>Misión</h3>
              <p>Crear música que resuene con personas de todos los orígenes, fomentando un sentido de comunidad y empoderamiento a través de nuestro arte. Nuestro objetivo es difundir mensajes positivos: unidad, amor y justicia social.</p>
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
