"""Abstract base class for AI message providers."""

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Abstract AI provider interface.

    All providers must implement generate_message() and support
    use as async context managers.
    """

    @abstractmethod
    async def generate_message(
        self,
        song_title: str,
        song_author: str,
    ) -> str:
        """Generate a message of the day.

        Args:
            song_title: Title of the featured song
            song_author: Author/artist of the featured song

        Returns:
            Generated message text (Spanish, 2-3 sentences, with emoji)
        """
        pass

    def _build_prompt(self, song_title: str, song_author: str) -> str:
        """Shared prompt template used by all providers."""
        return (
            f"Genera un mensaje del día para Séptima Ola, una banda de "
            f"reggae/ska/rocksteady de La Raza, Ciudad de México.\n\n"
            f"Contexto:\n"
            f'- Canción destacada: "{song_title}" por {song_author}\n\n'
            f"Requisitos:\n"
            f"- El mensaje debe ser inspirador, positivo y relacionado con la música\n"
            f"- Longitud: 2-3 oraciones\n"
            f"- Tono: cercano, auténtico, con groove\n"
            f"- Incluye un emoji musical apropiado\n"
            f"- Idioma: español\n\n"
            f"Genera solo el mensaje, sin encabezados ni formato adicional."
        )

    @abstractmethod
    async def close(self) -> None:
        """Release any held resources (HTTP clients, tokens, etc.)."""
        pass

    async def __aenter__(self) -> "AIProvider":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
