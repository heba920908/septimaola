import React from 'react'

export default function Discography() {
  const songs = [
    {
      title: 'Desde mi Ventana',
      description: 'Un viaje melódico que captura la esencia del reggae contemplativo con armonías ska.'
    },
    {
      title: 'Despertar',
      description: 'Llamada a la conciencia social con ritmos vibrantes y mensajes de transformación.'
    },
    {
      title: 'Arenga',
      description: 'Energía pura. Un grito de unidad y resistencia que resuena en el corazón del movimiento.'
    },
    {
      title: 'Contraluz',
      description: 'Melodía introspectiva que juega entre luces y sombras, explorando las paradojas de la existencia.'
    }
  ]

  return (
    <section id="musica" className="section-discography">
      <div className="container">
        <h2>Discografía / Material</h2>
        <div className="songs-grid">
          {songs.map((song, index) => (
            <div key={index} className="song-card">
              <h3>{song.title}</h3>
              <p>{song.description}</p>
              <div className="song-streaming">
                <a href="https://open.spotify.com/search" target="_blank" rel="noopener noreferrer">Spotify</a>
                <a href="https://bandcamp.com" target="_blank" rel="noopener noreferrer">Bandcamp</a>
                <a href="https://youtube.com" target="_blank" rel="noopener noreferrer">YouTube</a>
              </div>
            </div>
          ))}
        </div>
        <div className="discography-note">
          <p><strong>Material técnico:</strong> Masters y maquetas disponibles a solicitud para prensa y promociones.</p>
        </div>
      </div>
    </section>
  )
}
