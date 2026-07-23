"""Configuration for Séptima Ola social media automation."""

from dataclasses import dataclass
from typing import List


@dataclass
class VideoAsset:
    """Represents a video stored in Google Drive."""

    slug: str
    drive_id: str
    title: str
    author: str

    @property
    def public_url(self) -> str:
        """Generate Google Drive direct download URL."""
        return f"https://drive.google.com/uc?export=download&id={self.drive_id}"


# Video assets - direct video files from Google Drive
VIDEOS_CONFIG: List[VideoAsset] = [
    # TODO: Populate with actual Google Drive IDs for videos
    # VideoAsset("la_estacion", "DRIVE_ID_HERE", "La Estación", "Séptima Ola"),
    # VideoAsset("aguita_de_coco", "DRIVE_ID_HERE", "Agüita de Coco", "Séptima Ola"),
    # VideoAsset("salsa_callejera", "DRIVE_ID_HERE", "Salsa Callejera", "Séptima Ola"),
]

# Hashtags to include in posts
HASHTAGS: List[str] = [
    "#SéptimaOla",
    "#Reggae",
    "#Ska",
    "#Rocksteady",
    "#MusicaMexicana",
    "#LaRaza",
    "#CDMX",
]

# AI provider selection
# Set AI_PROVIDER env var to "deepseek" (default) or "codemie"
AI_PROVIDER_DEFAULT = "deepseek"

# Deepseek configuration
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-flash"

# Codemie configuration
# All values are read from environment variables; these are just doc references.
# CODEMIE_BASE_URL      - Base URL of the Codemie instance
# CODEMIE_KEYCLOAK_URL  - Keycloak base URL
# CODEMIE_REALM         - Keycloak realm name
# CODEMIE_CLIENT_ID     - Keycloak client ID
# CODEMIE_CLIENT_SECRET - Keycloak client secret
# CODEMIE_ASSISTANT_ID  - UUID of the Codemie assistant to call

# Facebook/Instagram API
FACEBOOK_API_VERSION = "v18.0"
FACEBOOK_BASE_URL = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}"
