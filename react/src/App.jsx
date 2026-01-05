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
