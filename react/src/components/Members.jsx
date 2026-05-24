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
      name: 'Alfred YearckLei',
      role: 'Guitarrista, Vocalista y Compositor',
      image: '1NLXEkoOz8CcVXXAFOMoCwttNoPVw7t35',
      imagePosition: 'top',
      shortDescription: 'Fundador, guitarrista, vocalista y compositor. Lidera Séptima Ola con 18 años de trayectoria musical.',
      fullDescription: 'Alfred YearckLei (nacido el 23 de enero de 1992) es el fundador, guitarrista, vocalista y compositor de Séptima Ola. Originario de la Ciudad de México, posee 18 años de trayectoria musical. Su formación incluye estudios de guitarra rock, blues y jazz con maestros reconocidos como Javier Stone y Jorge Cárdenas, así como entrenamiento vocal en el Faro Indios Verdes. Influenciado por artistas como The Skatalites, Dave Grohl y Daniel Gutierrez, Alfred domina géneros que van desde el reggae y rocksteady hasta el jazz y la trova.\n\nAntes de fundar Séptima Ola, trabajó en proyectos como Soul Lions (grabó "Soul Steady"), Arthur en sus días, y Ritmo Nacional. En colaboración con Levi (saxofón) y Rodrigo (violín), decidió iniciar Séptima Ola para crear música de calidad que conectara con los oyentes. Como compositor y arreglista, Alfred aporta versatilidad rítmica, melódica y lírica al grupo. Su misión personal resume su esencia: "Crear música, crear arte". Además, como curiosidad, su música favorita es el rap, y cuenta con una maqueta de rap lanzada a los 17 años con 13 canciones actualmente disponibles en Spotify bajo el nombre Yearck Lei.'
    },
    {
      name: 'lemanu / lemanubeats',
      role: 'Baterista',
      image: '1vZxL4byBgKMExxKbakuZhEgQ2hsFDPVY',
      imagePosition: 'top',
      shortDescription: 'Baterista originario de Cuajimalpa con 2 años 9 meses de trayectoria. Fusiona reggae y rock con sensibilidad rítmica.',
      fullDescription: 'lemanu es un baterista originario de Cuajimalpa, Ciudad de México, con 2 años 9 meses de trayectoria musical iniciada en 2023. Su formación comenzó en el taller de batería de la FARO Indios Verdes, donde desarrolló sus primeros pasos en el instrumento. Actualmente estudia en la Escuela de Música del Rock a la Palabra, donde profundiza en lectura rítmica, rudimentos, groove e improvisación.\n\nSu sonido está influenciado por bandas como The Police, Caifanes, Twenty One Pilots y Linkin Park, admirando a bateristas destacados como Stewart Copeland, Alfonso André, John Bonham, Josh Dun y Jeff Porcaro. Se define por una aproximación que integra el ritmo como elemento social y corporal, incorporando malabares y danza contemporánea en su inspiración rítmica.\n\nFue invitado a Séptima Ola por Sandy Robinsuell, con quien comparte trayectoria en la FARO Indios Verdes. En la banda, construye la base rítmica con grooves sólidos que generan conexión entre el bajo y la percusión, aportando una base esencial para el sonido característico de Séptima Ola.'
    },
    {
      name: 'Levi\'Sax',
      role: 'Saxofón Tenor',
      image: '1kh42JDOOif795zfIgig1c3THcWXdvsYq',
      imagePosition: 'top',
      shortDescription: 'Saxofonista del Estado de México con más de 10 años de trayectoria. Maestro y compositor.',
      fullDescription: 'Levi\'Sax es saxofonista tenor del Estado de México con más de 10 años de experiencia. Su formación ha sido mayormente autodidacta, manteniendo un aprendizaje activo mediante recursos libres, masterclass, cursos, libros y contenidos online. Ha trabajado con maestros reconocidos como Tito Hinojosa (España) y Sebastián Clementin (Argentina), ampliando sus horizontes musicales.\nSus influencias principales incluyen a saxofonistas como Eric Marienthal y Jean-Denis Michat, así como bandas como Tokio Ska, Zona Ganjah, The Skatalites y Alton Ellis. Géneros favoritos que han moldeado su sonido: jazz, ska, trova y folclore. Anteriormente fue miembro de Soul Lions antes de llegar a Séptima Ola tras salir de una banda anterior junto a Alfred (guitarra) y Rodrigo (violín).\nEn la banda, Levi contribuye en composición, arreglos y producción. Su valor único radica en aportar opinión crítica y creatividad, aspectos que considera raros en el grupo y parte de su singularidad. Ha presentado sus proyectos como solista en escenarios destacados como la Sala José León Portilla del Centro Cultural México Bicentenario, siendo cofundador y maestro de saxofón y flauta traversa en la orquesta infantil y juvenil O.S.I.N Xochipilli.'
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
      name: 'Sandy Robinsuell',
      role: 'Vocalista y Tecladista',
      image: '1EfbO0_BJL924CbnvjxfwbDaUj6Vo3uhp',
      imagePosition: 'center',
      shortDescription: 'Tecladista y vocalista corista. Licenciada en Psicología con técnica y sensibilidad artística.',
      fullDescription: 'Sandy Robinsuell es tecladista y vocalista corista de Séptima Ola, egresada de la Facultad de Psicología. Su camino musical comenzó desde la infancia, cuando cantaba para su madre como su primera espectadora. Esa pasión creció con ella y se extendió a su entorno, llegando a sus amigos y compañeros de la Facultad, donde su formación académica en Psicología enriqueció su mirada humana y creativa. \nA los 12 años inició sus prácticas en teclado junto a una de sus primas, quien sigue siendo parte fundamental de su vida y su arte. Se integró al coro de la FARO Indios Verdes, etapa que le brindó disciplina vocal, experiencia escénica y una profunda conexión con el trabajo colectivo. Durante la pandemia desarrolló "Puente Mágico", un canal de jam en vivo donde colaboró con cantantes y músicos de distintos países, explorando nuevas sonoridades, improvisación y comunidades creativas globales. A los 22 años fue invitada a trabajar en primeras maquetas profesionales, abriendo la puerta a proyectos sólidos que culminaron en su participación en Séptima Ola.\n Hoy, Robinsuell combina técnica y sensibilidad en la interpretación. Su aporte musical construye puentes sonoros desde lo íntimo hacia lo colectivo, aportando textura, emoción y atmósfera al sonido de la banda.'
    },
    {
      name: 'Arthur',
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
              <div className="member-card-body">
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
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
