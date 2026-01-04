import React from 'react'
import logo from '../assets/logo.png'

export default function Hero() {
  return (
    <section className="hero">
      <div className="hero-content">
        <img src={logo} alt="SÉPTIMA OLA" className="hero-logo"/>
        <p className="subtitle">Reggae · Ska · Rocksteady — Ciudad de México</p>
        <p className="lead">Press kit oficial — Material para prensa y promotores</p>
      </div>
    </section>
  )
}
