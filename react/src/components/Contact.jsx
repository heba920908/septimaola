import React from 'react'

export default function Contact() {
  return (
    <section id="contacto" className="section-contact">
      <div className="container">
        <h2>Contacto</h2>
        <div className="contact-content">
          <div className="contact-info">
            <p><strong>Booking:</strong> <a href="mailto:septimaolaoficial@gmail.com">septimaolaoficial@gmail.com</a></p>
            <p><strong>Prensa:</strong> <a href="mailto:septimaolaoficial@gmail.com">septimaolaoficial@gmail.com</a></p>
            <p><strong>Redes Sociales:</strong> @septimaolaoficial</p>
            <ul className="social-links">
              <li><a href="https://instagram.com/septimaolaoficial" target="_blank" rel="noopener noreferrer">Instagram</a></li>
              <li><a href="https://facebook.com/septimaolaoficial" target="_blank" rel="noopener noreferrer">Facebook</a></li>
              <li><a href="https://youtube.com/septimaolaoficial" target="_blank" rel="noopener noreferrer">YouTube</a></li>
            </ul>
            <p className="location"><strong>Base:</strong> Ciudad de México, México</p>
          </div>
          <p className="contact-note">Para entrevistas, fechas y material adicional (MP3, WAV, fotos, logos), por favor contacta a los correos anteriores.</p>
        </div>
      </div>
    </section>
  )
}
