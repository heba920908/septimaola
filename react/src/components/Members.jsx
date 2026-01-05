import React from 'react'

export default function Members() {
  const members = [
    {
      name: 'Sandy Robinsuell',
      role: 'Vocalista y Tecladista',
      image: '11URa6v_EjHpjz9s23eAo8siVFfbRcLkc',
      imagePosition: 'center', // center, top, bottom
      description: 'Formada en FARO Indios Verdes, egresada de Psicología y creadora del canal "Puente Mágico". Combina técnica coral, sensibilidad y texturas atmosféricas que elevan el sello emocional de Séptima Ola.'
    },
    {
      name: 'Itzel BP',
      role: 'Percusionista',
      image: '1NyA4KL3OsFB9m2W4u6JS7qcTJ_5-K3Mq',
      imagePosition: 'center',
      description: 'Especializada en congas, bongós y percusión latina. Sus raíces en salsa y cumbia se mezclan con el reggae y ska para aportar dinamismo y conexión con el público.'
    },
    {
      name: 'Alfred Herrera',
      role: 'Vocalista y Guitarrista',
      image: '1NLXEkoOz8CcVXXAFOMoCwttNoPVw7t35',
      imagePosition: 'top',
      description: 'Con influencias de Bob Marley y The Skatalites. Lidera la visión creativa y los mensajes de unidad, amor y justicia social de Séptima Ola.'
    },
    {
      name: 'Lemanu',
      role: 'Baterista',
      image: '1vZxL4byBgKMExxKbakuZhEgQ2hsFDPVY',
      imagePosition: 'top',
      description: 'Mezcla fluidez reggae con presencia rockera. Estudia en la Escuela de Música del Rock a la Palabra y construye grooves sólidos que sostienen los cambios dinámicos del show.'
    },
    {
      name: 'Levi',
      role: 'Saxofón Tenor',
      image: '1kh42JDOOif795zfIgig1c3THcWXdvsYq',
      imagePosition: 'top',
      description: 'Del Estado de México con más de 10 años de trayectoria. Fundó "Jazz & Love" y es maestro en la orquesta O.S.I.N Xochipilli.'
    },
    {
      name: 'Rodrigo Mera',
      role: 'Violinista',
      image: '1EXP5Kh_RfxbQLrNVMUn7-Fygg1LrC7Xw',
      imagePosition: 'top',
      description: 'Fundador con 11+ años de formación académica en la Sinfónica de la UACM. Integra el violín en ska/reggae con arreglos únicos.'
    },
    {
      name: 'Arthur Mono',
      role: 'Bajista',
      image: '10nWFvuwRtm_hR9LMtT5SmwRO5NCWey30',
      imagePosition: 'center', // Focus on top of the image
      description: 'Con raíces en la salsa. Su mezcla de ritmos caribeños y reggae añade profundidad y groove a cada arreglo.'
    }
  ]

  const getGoogleDriveImageUrl = (fileId) => {
    if (!fileId || fileId === 'PLACEHOLDER_ID') return null
    return `https://lh3.googleusercontent.com/d/${fileId}=w400-h400-c`
  }

  return (
    <section id="integrantes" className="section-members">
      <div className="container">
        <h2>Integrantes</h2>
        <div className="members-grid">
          {members.map((member, idx) => (
            <div key={idx} className="member-card">
              {member.image && member.image !== 'PLACEHOLDER_ID' && (
                <img 
                  src={getGoogleDriveImageUrl(member.image)} 
                  alt={member.name} 
                  className="member-image" 
                  style={{ objectPosition: member.imagePosition || 'center' }}
                  onError={(e) => {e.target.style.display = 'none'}} 
                />
              )}
              <h3>{member.name}</h3>
              <p className="role">{member.role}</p>
              <p className="description">{member.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
