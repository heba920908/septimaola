import React from 'react'
import { motion } from 'framer-motion'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.2,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      ease: [0.16, 1, 0.3, 1],
    },
  },
}

// Stage position data aligned with SKILL.md canonical placement
const stagePositions = [
  { id: 'arthur', name: 'Arthur', role: 'Bajo', emoji: '🎸', zone: 'left' },
  { id: 'sandy', name: 'Sandy', role: 'Voz Principal', emoji: '🎹', zone: 'left' },
  { id: 'alfred', name: 'Alfred Herrera', role: 'Guitarra / Voz Principal', emoji: '🎸', zone: 'center-front' },
  { id: 'lemanu', name: 'lemanu', role: 'Batería', emoji: '🥁', zone: 'rear-center' },
  { id: 'levisax', name: 'Levi\'Sax', role: 'Saxofón', emoji: '🎷', zone: 'right' },
  { id: 'rodrigo', name: 'Rodrigo Mera', role: 'Violín', emoji: '🎻', zone: 'right' },
]

function StagePerformerCard({ performer }) {
  return (
    <motion.div
      className="stage-performer"
      variants={itemVariants}
      whileHover={{ scale: 1.05, y: -4 }}
    >
      <div className="stage-performer-emoji">{performer.emoji}</div>
      <div className="stage-performer-name">{performer.name}</div>
      <div className="stage-performer-role">{performer.role}</div>
    </motion.div>
  )
}

function StageDiagram() {
  const leftPerformers = stagePositions.filter(p => p.zone === 'left')
  const centerFront = stagePositions.filter(p => p.zone === 'center-front')
  const rearCenter = stagePositions.filter(p => p.zone === 'rear-center')
  const rightPerformers = stagePositions.filter(p => p.zone === 'right')

  return (
    <motion.div className="stage-diagram" variants={itemVariants}>
      <div className="stage-frame">
        {/* Stage Left */}
        <div className="stage-zone stage-left">
          <div className="stage-zone-label">Lado Izquierdo</div>
          <div className="stage-performer-list">
            {leftPerformers.map(p => <StagePerformerCard key={p.id} performer={p} />)}
          </div>
        </div>

        {/* Center column: rear (drums) + front (guitar) */}
        <div className="stage-zone stage-center">
          <div className="stage-rear">
            <div className="stage-zone-label">Trasera Central</div>
            <div className="stage-performer-list">
              {rearCenter.map(p => <StagePerformerCard key={p.id} performer={p} />)}
            </div>
          </div>
          <div className="stage-front">
            <div className="stage-zone-label">Centro Frontal</div>
            <div className="stage-performer-list">
              {centerFront.map(p => <StagePerformerCard key={p.id} performer={p} />)}
            </div>
          </div>
        </div>

        {/* Stage Right */}
        <div className="stage-zone stage-right">
          <div className="stage-zone-label">Lado Derecho</div>
          <div className="stage-performer-list">
            {rightPerformers.map(p => <StagePerformerCard key={p.id} performer={p} />)}
          </div>
        </div>
      </div>

      {/* Audience/FOH indicator */}
      <motion.div className="stage-audience" variants={itemVariants}>
        <div className="stage-audience-arrow">↓</div>
        <div className="stage-audience-label">Audiencia — FOH (~20 m)</div>
        <div className="stage-audience-line"></div>
      </motion.div>
    </motion.div>
  )
}

export default function StagePlot() {
  const stageOrientation = [
    'La audiencia está frente al escenario.',
    'La posición del FOH debe estar centrada a aproximadamente 20 m del frente del escenario y a unos 1 m de altura.',
    'La batería permanece en la parte trasera central como ancla de tiempo.'
  ]

  const stagePlacement = [
    'Lado Izquierdo del Escenario (desde la vista de la audiencia): Arthur (Bajo), Sandy (Teclado/Voz de Apoyo)',
    'Centro Frontal: Alfred Herrera (Guitarra / Voz Principal)',
    'Parte Trasera Central: lemanu (Batería)',
    'Lado Derecho del Escenario: Rodrigo Mera (Violín), Levi\'Sax (Saxofón)'
  ]

  const monitorMixLayout = [
    {
      mix: 'Mix 1 (Batería)',
      channels: 'Bombo, Caja, Overhead, Referencia de Bajo',
      users: 'lemanu, Arthur'
    },
    {
      mix: 'Mix 2 (Primera línea)',
      channels: 'Bajo, Guitarra, Violín, Saxofón, teclados/voces selectivas según sea necesario',
      users: 'Alfred, Rodrigo, Levi\'Sax, Sandy'
    },
    {
      mix: 'Mix 3 (Referencia de Teclados/Voz)',
      channels: 'Prioridad para teclados y voces de apoyo',
      users: 'Sandy'
    }
  ]

  const inputToPositionMapping = [
    'Canal 1 Bombo -> Parte Trasera Central (Batería) -> Mix 1',
    'Canal 2 Caja -> Parte Trasera Central (Batería) -> Mix 1',
    'Canal 3 Overhead -> Parte Trasera Central (Batería) -> Mix 1',
    'Canal 4 Bajo -> Lado Izquierdo -> Mix 1 / Mix 2',
    'Canal 5 Guitarra -> Centro Frontal -> Mix 2',
    'Canal 6 Teclado Izq -> Lado Izquierdo -> Mix 2 / Mix 3',
    'Canal 7 Teclado Der o Voz de Apoyo -> Lado Izquierdo -> Mix 2 / Mix 3',
    'Canal 8 Violín -> Lado Derecho -> Mix 2',
    'Canal 9 Saxofón -> Lado Derecho -> Mix 2 (se requiere compresión)'
  ]

  const technicalNotes = [
    'Capacidad mínima de consola en el escenario: 8 canales con suficientes buses auxiliares para distribución de monitores; se prefieren 9 canales para mantener todas las entradas listadas discretas.',
    'Usar DI activas para Bajo, Teclados, Violín y Saxofón cuando sea posible.',
    'La guitarra y el bajo pueden usar DI o micrófonos de amplificador basados en el inventario del lugar.',
    'El sistema de monitores debe incluir control anti-retroalimentación.',
    'La salida objetivo del sistema permanece en al menos 100 dB SPL.'
  ]

  return (
    <motion.div
      id="stage-plot"
      className="presskit-subsection"
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-100px' }}
    >
      <motion.h3 variants={itemVariants}>Diagrama del Escenario</motion.h3>

      {/* Visual Stage Diagram */}
      <StageDiagram />

      <motion.div className="stage-subsection" variants={itemVariants}>
        <h4>Orientación del Escenario</h4>
        <ul className="presskit-list">
          {stageOrientation.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </motion.div>

      <motion.div className="stage-subsection" variants={itemVariants}>
        <h4>Ubicación Preferida en el Escenario</h4>
        <ul className="presskit-list">
          {stagePlacement.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </motion.div>

      <motion.div className="stage-subsection" variants={itemVariants}>
        <h4>Distribución de Mezclas de Monitores</h4>
        <div className="monitor-table-container">
          <table className="presskit-table">
            <thead>
              <tr>
                <th>Mix</th>
                <th>Canales</th>
                <th>Usuarios Principales</th>
              </tr>
            </thead>
          <tbody>
            {monitorMixLayout.map((mix, index) => (
              <tr key={index}>
                <td data-label="Mix">{mix.mix}</td>
                <td data-label="Canales">{mix.channels}</td>
                <td data-label="Usuarios">{mix.users}</td>
              </tr>
            ))}
          </tbody>
          </table>
        </div>
      </motion.div>

      <motion.div className="stage-subsection" variants={itemVariants}>
        <h4>Mapeo de Entradas a Posiciones (Referencia)</h4>
        <ul className="presskit-list">
          {inputToPositionMapping.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </motion.div>

      <motion.div className="stage-subsection" variants={itemVariants}>
        <h4>Notas Técnicas</h4>
        <ul className="presskit-list">
          {technicalNotes.map((note, index) => (
            <li key={index}>{note}</li>
          ))}
        </ul>
      </motion.div>
    </motion.div>
  )
}
