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

export default function InputList() {
  const inputChannels = [
    { 
      channel: '1', 
      instrument: 'Bombo', 
      micDi: 'Mic dinámico', 
      aux: 'Mix 1 (Batería)', 
      equipment: 'Soporte para mic de batería', 
      notes: 'Requerido' 
    },
    { 
      channel: '2', 
      instrument: 'Caja', 
      micDi: 'Mic dinámico', 
      aux: 'Mix 1 (Batería)', 
      equipment: 'Soporte para mic de batería', 
      notes: 'Requerido' 
    },
    { 
      channel: '3', 
      instrument: 'Overhead (Batería)', 
      micDi: 'Mic de condensador', 
      aux: 'Mix 1 (Batería)', 
      equipment: 'Soporte boom + phantom power', 
      notes: 'Puede ser mono si los canales son limitados' 
    },
    { 
      channel: '4', 
      instrument: 'Bajo', 
      micDi: 'DI (preferido) o mic de amp', 
      aux: 'Mix 1 / Mix 2', 
      equipment: 'Caja DI activa o amp de bajo', 
      notes: 'Se requiere DI o amplificador de monitor' 
    },
    { 
      channel: '5', 
      instrument: 'Guitarra', 
      micDi: 'DI o mic de amp', 
      aux: 'Mix 2 (Primera línea)', 
      equipment: 'Caja DI o amp de guitarra', 
      notes: 'Se requiere DI o amplificador de monitor' 
    },
    { 
      channel: '6', 
      instrument: 'Teclado Izq', 
      micDi: 'DI', 
      aux: 'Mix 2 / Mix 3', 
      equipment: 'Caja DI activa', 
      notes: 'Si es necesario, puede sumarse a mono' 
    },
    { 
      channel: '7', 
      instrument: 'Teclado Der / Voz de Apoyo', 
      micDi: 'DI o mic dinámico vocal', 
      aux: 'Mix 2 / Mix 3', 
      equipment: 'Caja DI o mic vocal + soporte', 
      notes: 'Usar como teclado derecho cuando esté disponible el estéreo' 
    },
    { 
      channel: '8', 
      instrument: 'Violín', 
      micDi: 'DI', 
      aux: 'Mix 2 (Primera línea)', 
      equipment: 'Caja DI activa', 
      notes: 'Se requiere DI' 
    },
    { 
      channel: '9', 
      instrument: 'Saxofón', 
      micDi: 'DI o mic de clip', 
      aux: 'Mix 2 (Primera línea)', 
      equipment: 'Caja DI o mic de sax + compresor', 
      notes: 'Se requiere compresión' 
    }
  ]

  return (
    <motion.div
      id="inputs"
      className="presskit-subsection"
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-100px' }}
    >
      <motion.h3 variants={itemVariants}>Input List / Lista de Canales</motion.h3>
      
      <motion.div className="input-table-container" variants={itemVariants}>
        <table className="presskit-table">
          <thead>
            <tr>
              <th>Canal</th>
              <th>Instrumento</th>
              <th>Mic/DI</th>
              <th>Aux</th>
              <th>Equipo</th>
              <th>Notas</th>
            </tr>
          </thead>
          <tbody>
            {inputChannels.map((channel, index) => (
              <tr key={index}>
                <td>{channel.channel}</td>
                <td>{channel.instrument}</td>
                <td>{channel.micDi}</td>
                <td>{channel.aux}</td>
                <td>{channel.equipment}</td>
                <td>{channel.notes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </motion.div>
    </motion.div>
  )
}