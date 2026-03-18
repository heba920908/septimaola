import React from 'react'
import logo from '../assets/logo.png'

export default function Hero() {
  return (
    <section className="hero">
      <div className="hero-content">
        <img src={logo} alt="SÉPTIMA OLA" className="hero-logo"/>
        <p className="subtitle">Reggae · Ska · Rocksteady — Ciudad de México</p>
        <p className="lead">Press kit oficial — Material para prensa y promotores</p>

        <a
          className="btn btn-primary presskit-btn"
          href="https://mega.nz/file/zoYB1DyI#jXOpxEf3_8e7mI8ZvLaL8V8sKJd0VbIKtfz30i7mt-g"
          target="_blank"
          rel="noopener noreferrer"
          download
        >
          Descargar Presskit
        </a>
      </div>
    </section>
  )
}
