import React from 'react'

export default function Section({ id, title, children }) {
  return (
    <section id={id} className="section">
      <div className="container">
        <h2>{title}</h2>
        <div>{children}</div>
      </div>
    </section>
  )
}
