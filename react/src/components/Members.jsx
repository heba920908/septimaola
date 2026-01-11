import React, { useState, useEffect, useRef } from 'react'

// Component to handle image loading with retry logic for 429 errors
// Leverages browser HTTP cache - uses cached images when available, retries on errors
function ImageWithRetry({ src, alt, className, style, imagePosition }) {
  const [retryCount, setRetryCount] = useState(0)
  const [shouldShow, setShouldShow] = useState(true)
  const retryTimeoutRef = useRef(null)
  const maxRetries = 2

  useEffect(() => {
    // Reset when src changes
    if (src) {
      setRetryCount(0)
      setShouldShow(true)
    }
    
    return () => {
      // Cleanup timeout on unmount or src change
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current)
      }
    }
  }, [src])

  const handleError = (e) => {
    if (retryCount < maxRetries) {
      // Incremental delay: 1s for first retry, 2s for second retry
      const delay = (retryCount + 1) * 1000
      
      retryTimeoutRef.current = setTimeout(() => {
        setRetryCount(prev => prev + 1)
        // Simply trigger a re-render by updating retryCount
        // Browser will use cache if available, or make fresh request if not
        // No need to clear/reset src - browser handles caching automatically
      }, delay)
    } else {
      // Max retries reached, hide image
      setShouldShow(false)
      if (e.target) {
        e.target.style.display = 'none'
      }
    }
  }

  const handleLoad = () => {
    // Successfully loaded, clear any pending retries
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current)
    }
    // Reset retry count on successful load
    setRetryCount(0)
  }

  if (!src || src === 'PLACEHOLDER_ID' || !shouldShow) return null

  return (
    <img 
      src={src} 
      alt={alt} 
      className={className} 
      style={{ 
        ...style, 
        objectPosition: imagePosition || 'center'
      }}
      onError={handleError}
      onLoad={handleLoad}
      key={`${src}-${retryCount}`} // Key change forces re-render on retry
    />
  )
}

export default function Members() {
  const [expandedMember, setExpandedMember] = useState(null)

  const members = [
    {
      name: 'Sandy Robinsuell',
      role: 'Vocalista y Tecladista',
      image: '11URa6v_EjHpjz9s23eAo8siVFfbRcLkc',
      imagePosition: 'center',
      shortDescription: 'Vocalista y tecladista. Combina técnica coral y texturas atmosféricas.',
      fullDescription: 'Vocalista corista de Séptima Ola. Su camino musical comenzó desde la infancia, cuando cantaba para su madre como su primera espectadora. Esa pasión creció con ella y se extendió a su entorno, llegando a sus amigos y compañeros de la Facultad de Psicología, carrera de la que también es egresada y que forma parte esencial de su mirada humana y creativa. A los 12 años inició sus prácticas en teclado junto a una de sus primas, quien hoy sigue siendo parte fundamental de su vida y su arte. Tiempo después se integró al coro de la FARO Indios Verdes, etapa que le brindó disciplina vocal, experiencia escénica y una profunda conexión con el trabajo colectivo. Durante la pandemia desarrolló "Puente Mágico", un canal de jam en vivo donde colaboró con cantantes y músicos de distintos países, explorando nuevas sonoridades, improvisación y comunidades creativas globales. A los 22 años, un amigo estudiante de la Facultad de Música la invitó a trabajar en sus primeras maquetas profesionales, abriendo así la puerta a proyectos cada vez más sólidos y a su participación en la banda Séptima Ola. Hoy, Robinsuell combina técnica, sensibilidad y una vocación profunda por la expresión artística. Su estilo tecladístico atmosférico y su aportación vocal añaden textura y emoción al sello musical de Séptima Ola.'
    },
    {
      name: 'Itzel BP',
      role: 'Percusionista',
      image: '1NyA4KL3OsFB9m2W4u6JS7qcTJ_5-K3Mq',
      imagePosition: 'center',
      shortDescription: 'Percusionista especializada en congas y bongós. Fusiona ritmos latinos con reggae y ska.',
      fullDescription: 'Percusionista de Séptima Ola, aportando ritmos vibrantes y una energía contagiosa que eleva la música de la banda. Su pasión por la percusión comenzó en su juventud, explorando diversos estilos y técnicas que ahora enriquecen el sonido único del grupo. Su especialidad en instrumentos como congas, bongós y otros elementos de percusión latina comenzó en la música salsa y cumbia, y ahora se fusionan perfectamente con los ritmos reggae y ska de Séptima Ola. Itzel BP no solo aporta su habilidad técnica, sino también una presencia escénica dinámica que conecta con el público, haciendo que cada presentación sea una experiencia inolvidable. Su dedicación y amor por la música son evidentes en cada ritmo que toca, contribuyendo significativamente al carácter distintivo de la banda.'
    },
    {
      name: 'Alfred Herrera',
      role: 'Vocalista y Guitarrista',
      image: '1NLXEkoOz8CcVXXAFOMoCwttNoPVw7t35',
      imagePosition: 'top',
      shortDescription: 'Fundador, guitarrista y vocalista. Lidera la visión creativa con mensajes de unidad y justicia social.',
      fullDescription: 'Alfred Herrera es el guitarrista y fundador de Séptima Ola, una banda que fusiona reggae, ska y rocksteady para crear un sonido único. Su viaje musical comenzó en la Ciudad de México, donde se sumergió en la escena local y desarrolló su estilo distintivo. Con influencias que van desde Bob Marley hasta The Skatalites, Alfred ha trabajado incansablemente para perfeccionar su técnica y llevar la música de Séptima Ola a audiencias de todo el mundo. Su enfoque creativo y su pasión por la música se reflejan en cada composición, haciendo de Séptima Ola una banda que no solo entretiene, sino que también inspira con mensajes de amor, unidad y justicia social. Destaca por su habilidad para combinar ritmos tradicionales con elementos modernos, creando un sonido fresco y relevante en la escena musical contemporánea.'
    },
    {
      name: 'Lemanu',
      role: 'Baterista',
      image: '1vZxL4byBgKMExxKbakuZhEgQ2hsFDPVY',
      imagePosition: 'top',
      shortDescription: 'Baterista que fusiona la fluidez del reggae con la presencia del rock.',
      fullDescription: 'Lemanu es un baterista que mezcla energía suave, firmeza rítmica y sensibilidad musical. Su estilo fusiona la fluidez del reggae con la presencia del rock. Actualmente estudia en la Escuela de Música del Rock a la Palabra, donde continúa desarrollando su técnica, su criterio musical y su lenguaje rítmico. Construye grooves sólidos que sostienen los cambios dinámicos del show, aportando una base rítmica esencial para el sonido característico de Séptima Ola.'
    },
    {
      name: 'Levi',
      role: 'Saxofón Tenor',
      image: '1kh42JDOOif795zfIgig1c3THcWXdvsYq',
      imagePosition: 'top',
      shortDescription: 'Saxofonista del Estado de México con más de 10 años de trayectoria.',
      fullDescription: 'Saxofonista del Estado de México con más de 10 años de experiencia. Su carrera musical se ha ido desarrollando en el Estado de México desde el 2005 aproximadamente con clases de guitarra en la secundaria, continuando de manera autodidacta y llegando a ensambles de cámara con prestaciones de ámbito cultural. Formó parte de bandas locales de rock, ska y reggae, llegando a grabar un disco con esta última. La búsqueda del sonido versátil del saxofón lo llevó a seguirse formando musicalmente en diferentes centros culturales locales, cursos, máster class y de manera particular con variados profesores, Tito Hinojosa desde España y Sebastián Clementin desde Argentina. Dando como resultado el seguir como solista en presentaciones privadas, y ya reconocido por impartir clases localmente, la Secretaría de Turismo del Estado de México lo buscó, llegando a una serie de presentaciones del llamado: "Concierto de saxofón, a mi manera", donde expuso algunas de las melodías más populares del jazz en diferentes centros culturales y casas de cultura, culminando en el auditorio Dr. Miguel León Portilla en el Centro Cultural México Bicentenario en Texcoco, Edo. Mex. Actualmente continúa con el proyecto como solista, ahora llamado "Jazz & Love", con presentaciones privadas, culturales y públicas. Es cofundador, saxofón tenor, maestro de saxofón y flauta traversa en la orquesta infantil y juvenil O.S.I.N Xochipilli con presentaciones culturales en el Estado de México y en la Ciudad de México.'
    },
    {
      name: 'Rodrigo Mera',
      role: 'Violinista',
      image: '1EXP5Kh_RfxbQLrNVMUn7-Fygg1LrC7Xw',
      imagePosition: 'top',
      shortDescription: 'Arreglista y Compositor',
      fullDescription: 'Licenciado por la Escuela de Bellas Artes de Nezahualcóyotl, Rodrigo aporta a Séptima Ola una sólida formación académica, colaborando activamente en la creación de la música y los arreglos del grupo. Su trayectoria incluye presentaciones en recintos como el Castillo de Chapultepec y la Biblioteca Vasconcelos, participando en orquestas como la Sinfónica de la UACM y la Metropolitana junto a artistas de renombre y solistas internacionales.\n\nComo productor independiente, su trabajo supera las 200,000 reproducciones en plataformas digitales. Además, dirige el proyecto EMVA, donde impulsa la formación musical de nuevos talentos que se presentan en los foros de las UTOPÍAS de la CDMX. En Séptima Ola, Rodrigo equilibra el rigor orquestal con la versatilidad de la producción contemporánea.'
    },
    {
      name: 'Arthur Mono',
      role: 'Bajista',
      image: '10nWFvuwRtm_hR9LMtT5SmwRO5NCWey30',
      imagePosition: 'center',
      shortDescription: 'Bajista apasionado por la salsa. Combina ritmos caribeños con reggae.',
      fullDescription: 'Arthur es un bajista apasionado por la salsa y sus ritmos contagiosos. Su viaje musical comenzó con Alfred en "Arthur en sus días", una banda de salsa que le permitió explorar y perfeccionar su técnica en el bajo. A lo largo de los años, Arthur ha desarrollado un estilo único que combina la energía vibrante de la salsa con la profundidad rítmica del reggae. Su mezcla de ritmos caribeños y reggae añade profundidad y groove a cada arreglo, aportando una base sólida y rica en texturas al sonido de Séptima Ola.'
    }
  ]

  const getGoogleDriveImageUrl = (fileId) => {
    if (!fileId || fileId === 'PLACEHOLDER_ID') return null
    return `https://lh3.googleusercontent.com/d/${fileId}=w400-h400-c`
  }

  const toggleExpand = (idx) => {
    setExpandedMember(expandedMember === idx ? null : idx)
  }

  return (
    <section id="integrantes" className="section-members">
      <div className="container">
        <h2>Integrantes</h2>
        <div className="members-grid">
          {members.map((member, idx) => (
            <div key={idx} className="member-card">
              {member.image && member.image !== 'PLACEHOLDER_ID' && (
                <ImageWithRetry
                  src={getGoogleDriveImageUrl(member.image)}
                  alt={member.name}
                  className="member-image"
                  imagePosition={member.imagePosition}
                />
              )}
              <h3>{member.name}</h3>
              <p className="role">{member.role}</p>
              <p className="description">
                {expandedMember === idx ? member.fullDescription : member.shortDescription}
              </p>
              <button 
                className="ver-mas-btn"
                onClick={() => toggleExpand(idx)}
              >
                {expandedMember === idx ? 'ver menos' : 'ver más'}
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
