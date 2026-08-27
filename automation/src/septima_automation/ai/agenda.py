"""Canonical event agenda for Séptima Ola with Pydantic typing.

This module provides structured representations of band events (concerts,
showcases, radio appearances, cultural presentations) used for correlation
with social media performance metrics.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AgendaEvent(BaseModel):
    """Represents a scheduled or completed band event."""

    date: str = Field(description="ISO 8601 date (YYYY-MM-DD)")
    time: Optional[str] = Field(default=None, description="Event time if known (e.g. 19:30)")
    title: str = Field(description="Event title or showcase name")
    venue: str = Field(description="Venue, location, or address")
    description: str = Field(default="", description="Description of the show and co-billing")
    event_type: str = Field(default="Concierto", description="Foro, Bar, Festival, Cultural, Familiar, etc.")
    objective: str = Field(default="Promoción", description="Promoción, Pagado, etc.")
    url: Optional[str] = Field(default=None, description="Event link, map link, or post URL")


AGENDA_2026: List[AgendaEvent] = [
    AgendaEvent(
        date="2026-05-14",
        time="17:30",
        title="Junket & Showcase de prensa",
        venue="Guadalajara 60, Roma Nte., Cuauhtémoc, CDMX",
        description="Rueda de medios, tocan dos bandas, dentro de ellas Séptima Ola",
        event_type="Foro",
        objective="Promoción",
    ),
    AgendaEvent(
        date="2026-05-15",
        time="19:30",
        title="Minifestival Skatepec",
        venue="Av. Insurgentes Manzana 1 Lote 6, El Calvario, Ecatepec de Morelos, Méx.",
        description="Evento de Ska en bar con La rebambaramba y Mayor Skala",
        event_type="Bar",
        objective="Promoción",
    ),
    AgendaEvent(
        date="2026-05-16",
        time="19:30",
        title="Ska en las montañas",
        venue="Sol 45, San Bartolo Ameyalco, Álvaro Obregón, CDMX",
        description="Evento de Ska con Royal Club y más bandas",
        event_type="Festival",
        objective="Promoción",
    ),
    AgendaEvent(
        date="2026-05-21",
        time="16:00",
        title="Séptima Ola Radio entrevista Armada Cultural",
        venue="Av. Huitzilihuitl 51, Santa Isabel Tola, Gustavo A. Madero, CDMX",
        description="Entrevista con Armada Cultural para SORadio",
        event_type="Cultural",
        objective="Promoción",
    ),
    AgendaEvent(
        date="2026-05-28",
        time="20:00",
        title="Concierto con La Matatena (michis y lomitos)",
        venue="Guadalajara 60, Roma Nte., Cuauhtémoc, CDMX",
        description="Evento con La Matatena y Colectivo Latino",
        event_type="Foro",
        objective="Promoción",
    ),
    AgendaEvent(
        date="2026-06-04",
        time="18:30",
        title="Entrevista en La Machincuepa Radio",
        venue="Zarco 115, Moctezuma esq. Guerrero, Cuauhtémoc, CDMX",
        description="Entrevista presencial en programa de radio por internet",
        event_type="Foro",
        objective="Promoción",
    ),
    AgendaEvent(
        date="2026-06-07",
        time="17:00",
        title="Batallas de Rap Convars",
        venue="Foro Mictlan",
        description="Show de 30 minutos antes de batalla estelar",
        event_type="Foro",
        objective="Promoción",
    ),
    AgendaEvent(
        date="2026-06-13",
        time="14:30",
        title="Acústico en FIV",
        venue="Av. Huitzilihuitl 51, Santa Isabel Tola, Gustavo A. Madero, CDMX",
        description="Show acústico en cabina de radio Faro IV",
        event_type="Cultural",
        objective="Promoción",
    ),
    AgendaEvent(
        date="2026-06-13",
        time="20:30",
        title="Presentación DESDE MI VENTANA en Capitán Gallo",
        venue="Ayuntamiento 145, Col Centro, CDMX",
        description="Presentación Desde mi ventana en Capitán Gallo",
        event_type="Foro",
        objective="Promoción",
    ),
    AgendaEvent(
        date="2026-06-20",
        time="19:00",
        title="Presentación en Bar - Los Haraganes Rock",
        venue="Arteaga 13, San Ángel, Álvaro Obregón, CDMX",
        description="Presentación en bar al sur de la CDMX junto a otras bandas para el promotor Attack Rock Show",
        event_type="Bar",
        objective="Promoción",
    ),
    AgendaEvent(
        date="2026-06-28",
        time="16:00",
        title="Fiesta patronal Cuajimalpa",
        venue="Cuajimalpa, CDMX",
        description="Presentación en fiesta patronal",
        event_type="Familiar",
        objective="Promoción",
    ),
    AgendaEvent(
        date="2026-07-04",
        time="12:00",
        title="Recital EMVA",
        venue="Utopía Teotongo, Iztapalapa, CDMX",
        description="Recital EMVA con invitados: Armada Cultural y Séptima Ola",
        event_type="Cultural",
        objective="Promoción",
    ),
    AgendaEvent(
        date="2026-07-05",
        time="14:00",
        title="Reggae y Ska en El Rule",
        venue="Centro Cultural El Rule, Centro Histórico, CDMX",
        description="Tarde de Reggae y Ska en el Rule con Los Cuxsons, Armada Cultural y Paino's Roots Band",
        event_type="Cultural",
        objective="Promoción",
    ),
    AgendaEvent(
        date="2026-07-18",
        time="14:00",
        title="Skandalazo Utópico con Armada Cultural",
        venue="Utopía Cuauhtlicalli, Iztapalapa, CDMX",
        description="Show con La Huelga, Armada Cultural, Séptima Ola y Sonora Jauría",
        event_type="Cultural",
        objective="Promoción",
    ),
    AgendaEvent(
        date="2026-07-24",
        time="21:00",
        title="Pulquería Insurgentes",
        venue="Pulquería Insurgentes, CDMX",
        description="Fiesta de ska y reggae",
        event_type="Bar",
        objective="Promoción",
    ),
    AgendaEvent(
        date="2026-07-25",
        time="15:00",
        title="5to Festival de las Serpientes",
        venue="Utopía Libertad, Iztapalapa, CDMX",
        description="Presentación en Utopía Libertad compartiendo escenario con Chakana",
        event_type="Familiar",
        objective="Promoción",
        url="https://www.facebook.com/UtopiaLibertadCdMex/posts/997009416659395/",
    ),
    AgendaEvent(
        date="2026-07-31",
        time="19:00",
        title="Vacas Verdes Bellas Artes",
        venue="Pulquería Vacas Verdes Bellas Artes, CDMX",
        description="Invitación de la pen-k a tocar en Vacas Verdes",
        event_type="Bar",
        objective="Promoción",
    ),
    AgendaEvent(
        date="2026-08-07",
        time="20:00",
        title="Radio Bahía Colossal Ska Orchestra en Gato Calavera",
        venue="Gato Calavera, CDMX",
        description="Presentación en Gato Calavera en Radio Bahía Colossal Ska Orchestra",
        event_type="Bar",
        objective="Promoción",
    ),
    AgendaEvent(
        date="2026-08-08",
        time="19:00",
        title="XV años Iztapalapa",
        venue="Iztapalapa, CDMX",
        description="Show privado durante banquete de XV años",
        event_type="Familiar",
        objective="Pagado",
    ),
    AgendaEvent(
        date="2026-08-13",
        time="11:00",
        title="Festival de las Juventudes 2026 (Colectivo / Insulini)",
        venue="Utopía Mixiuhca, Iztacalco, CDMX",
        description="Festival de las Juventudes INJUVE con Colectivo Latino, Insulini, Toque Cumbiero y Séptima Ola",
        event_type="Cultural",
        objective="Promoción",
    ),
    AgendaEvent(
        date="2026-08-20",
        time="10:00",
        title="Live session en Rock Titanio",
        venue="Estudio Grabación Titanio Records, CDMX",
        description="Presentación y live session en La Música en Movimiento con el Rod / Rock Titanio",
        event_type="Foro",
        objective="Promoción",
    ),
]
