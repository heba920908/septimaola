import React from 'react'
import Section from './Section'

const ALLOWED_EMBED_ORIGINS = [
  'https://www.facebook.com/plugins/',
]

function isAllowedEmbed(src) {
  return ALLOWED_EMBED_ORIGINS.some(origin => src.startsWith(origin))
}

const FB_PAGE_URL = 'https://www.facebook.com/septimaolaoficial'
const FB_PAGE_PLUGIN_SRC = `https://www.facebook.com/plugins/page.php?href=${encodeURIComponent(FB_PAGE_URL)}&tabs=timeline&small_header=false&adapt_container_width=true&hide_cover=false&show_facepile=false&width=500&height=700`

export default function News() {
  if (!isAllowedEmbed(FB_PAGE_PLUGIN_SRC)) {
    return null
  }

  return (
    <Section id="noticias" title="Noticias">
      <div className="news-fb-page">
        <iframe
          title="Noticias de Facebook"
          src={FB_PAGE_PLUGIN_SRC}
          loading="lazy"
          scrolling="no"
          frameBorder="0"
          allowFullScreen
          allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"
        />
      </div>
    </Section>
  )
}
