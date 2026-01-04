import React from 'react'

export default function Gallery() {
  const gallery = [
    {
      id: '19uaer0nzCFxDSXnsLbUQxiMTvsar7bWk',
      caption: 'Séptima Ola - Foto oficial 1'
    },
    {
      id: '1Dota0wNlio8W_4w7w8VuPa2IHGgnBcTD',
      caption: 'Séptima Ola - Foto oficial 2'
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
