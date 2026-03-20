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
          href="https://drive.google.com/file/d/1bV4JgTpkhVVMLHrzG9m4ke5q4n1Ts8hE/view?usp=sharing"
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
