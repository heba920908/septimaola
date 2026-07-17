import React from 'react'
import { motion } from 'framer-motion'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.12,
      delayChildren: 0.15,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.16, 1, 0.3, 1],
    },
  },
}

export default function PrivacyNotice() {
  const handleBackClick = (e) => {
    e.preventDefault()
    window.location.hash = ''
  }

  return (
    <div className="privacy-page">
      <div className="privacy-header">
        <div className="container">
          <motion.div className="back-link-container" variants={itemVariants}>
            <a href="#/" onClick={handleBackClick} className="back-link">
              ← Volver
            </a>
          </motion.div>

          <motion.div
            className="section-heading"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            <motion.h1 variants={itemVariants}>Aviso de Privacidad</motion.h1>
            <motion.div className="minimal-line" variants={itemVariants} />
          </motion.div>

          <motion.p className="impact-phrase" variants={itemVariants}>
            Transparencia sobre el tratamiento de datos personales en nuestros
            canales digitales
          </motion.p>
        </div>
      </div>

      <div className="container">
        <motion.nav
          className="privacy-navigation"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          aria-label="Secciones del aviso de privacidad"
        >
          <motion.a href="#responsable" variants={itemVariants} className="nav-link">
            Responsable
          </motion.a>
          <motion.a href="#datos" variants={itemVariants} className="nav-link">
            Datos recabados
          </motion.a>
          <motion.a href="#finalidades" variants={itemVariants} className="nav-link">
            Finalidades
          </motion.a>
          <motion.a href="#derechos" variants={itemVariants} className="nav-link">
            Derechos
          </motion.a>
          <motion.a href="#cookies" variants={itemVariants} className="nav-link">
            Cookies
          </motion.a>
          <motion.a href="#vigencia" variants={itemVariants} className="nav-link">
            Vigencia
          </motion.a>
        </motion.nav>

        <motion.section
          id="responsable"
          className="privacy-section"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.h2 variants={itemVariants}>1. Responsable</motion.h2>
          <motion.p variants={itemVariants}>
            Séptima Ola, con base en Ciudad de México, es responsable del uso y
            protección de la información que pudiera recibirse por medios
            oficiales de contacto.
          </motion.p>
          <motion.p variants={itemVariants}>
            Correo de contacto para este aviso: septimaolaoficial@gmail.com
          </motion.p>
        </motion.section>

        <motion.section
          id="datos"
          className="privacy-section"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.h2 variants={itemVariants}>2. Datos personales recabados</motion.h2>
          <motion.p variants={itemVariants}>
            Actualmente no recabamos datos personales a traves del sitio web.
          </motion.p>
          <motion.p variants={itemVariants}>
            Este sitio no incluye formularios de registro, suscripcion,
            contratacion, pagos ni mecanismos de captura de datos personales.
          </motion.p>
        </motion.section>

        <motion.section
          id="finalidades"
          className="privacy-section"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.h2 variants={itemVariants}>3. Finalidades del tratamiento</motion.h2>
          <motion.p variants={itemVariants}>
            No aplica por el momento, ya que no existe tratamiento de datos
            personales desde este sitio.
          </motion.p>

          <motion.h3 variants={itemVariants}>4. Base legal y consentimiento</motion.h3>
          <motion.p variants={itemVariants}>
            No aplica por el momento. En caso de que en el futuro se habiliten
            procesos de recoleccion de datos, se actualizara este aviso y se
            solicitara consentimiento cuando sea requerido por la normativa
            aplicable.
          </motion.p>

          <motion.h3 variants={itemVariants}>5. Transferencias de datos</motion.h3>
          <motion.p variants={itemVariants}>
            No aplica por el momento. No transferimos datos personales porque no
            los recabamos.
          </motion.p>
        </motion.section>

        <motion.section
          id="derechos"
          className="privacy-section"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.h2 variants={itemVariants}>6. Derechos ARCO y contacto</motion.h2>
          <motion.p variants={itemVariants}>
            Si en el futuro se llegaran a tratar datos personales, las personas
            titulares podran ejercer sus derechos de acceso, rectificacion,
            cancelacion y oposicion mediante solicitud al correo oficial:
            septimaolaoficial@gmail.com.
          </motion.p>

          <motion.h3 variants={itemVariants}>7. Conservacion</motion.h3>
          <motion.p variants={itemVariants}>
            No aplica por el momento. No conservamos datos personales desde este
            sitio.
          </motion.p>

          <motion.h3 variants={itemVariants}>8. Medidas de seguridad</motion.h3>
          <motion.p variants={itemVariants}>
            No aplica por el momento respecto de datos personales en este sitio,
            ya que no se recolectan ni almacenan.
          </motion.p>
        </motion.section>

        <motion.section
          id="cookies"
          className="privacy-section"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.h2 variants={itemVariants}>9. Cookies y tecnologias de rastreo</motion.h2>
          <motion.p variants={itemVariants}>
            Actualmente este sitio no implementa cookies propias para recabar
            datos personales ni herramientas de analitica propias.
          </motion.p>
          <motion.p variants={itemVariants}>
            Si en el futuro se incorporan tecnologias de rastreo, este aviso se
            actualizara para reflejar su uso y finalidad.
          </motion.p>

          <motion.h3 variants={itemVariants}>Uso de la app de Facebook registrada</motion.h3>
          <motion.p variants={itemVariants}>
            La app de Facebook asociada al proyecto esta registrada
            exclusivamente para fines de publicacion de contenido en redes
            sociales oficiales. No se utiliza para recolectar, perfilar o
            almacenar informacion personal de personas usuarias.
          </motion.p>
        </motion.section>

        <motion.section
          id="vigencia"
          className="privacy-section"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.h2 variants={itemVariants}>10. Cambios al aviso y vigencia</motion.h2>
          <motion.p variants={itemVariants}>
            Este aviso podra modificarse para reflejar cambios operativos,
            tecnicos o regulatorios. Cualquier actualizacion se publicara en esta
            misma seccion del sitio.
          </motion.p>
          <motion.p variants={itemVariants}>
            Fecha de ultima actualizacion: 16 de julio de 2026.
          </motion.p>
        </motion.section>
      </div>
    </div>
  )
}
