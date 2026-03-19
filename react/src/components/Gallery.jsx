import React from 'react'

export default function Gallery() {
  const gallery = [
    {
      id: '17NlhB47l-1RD9mlxM9hJpMwvSz1g8UEb',
      caption: 'Séptima Ola - Foto oficial 1'
    },
    {
      id: '1LmL-xTYYOU-jf1WVThT4N3Y9vLytwvWy',
      caption: 'Séptima Ola - Foto oficial 2'
    },
    {
      id: '1LmL-xTYYOU-jf1WVThT4N3Y9vLytwvWy',
      caption: 'Robinsuell'
    }
  ]

  const getGoogleDriveImageUrl = (fileId) => {
    if (!fileId) return null
    return `https://lh3.googleusercontent.com/d/${fileId}=w800-h600-c`
  }

  return (
    <section id="galeria" className="section-gallery">
      <div className="container">
        <h2>Galería</h2>
        <div className="gallery-grid">
          {gallery.map((photo, index) => (
            <img 
              key={index}
              src={getGoogleDriveImageUrl(photo.id)} 
              alt={photo.caption}
              onError={(e) => {e.target.style.display = 'none'}}
            />
          ))}
        </div>
        <p className="gallery-note">Fotos oficiales (alta resolución) y logos vectoriales disponibles bajo petición.</p>
      </div>
    </section>
  )
}
