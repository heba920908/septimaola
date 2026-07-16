"""Configuration for Séptima Ola social media automation."""

from dataclasses import dataclass
from typing import List


@dataclass
class ImageAsset:
    """Represents an image stored in Google Drive."""

    slug: str
    drive_id: str
    category: str  # "members", "gallery", "promo"

    @property
    def public_url(self) -> str:
        """Generate Google Drive direct URL."""
        return f"https://lh3.googleusercontent.com/d/{self.drive_id}"


@dataclass
class AudioAsset:
    """Represents a short audio clip stored in Google Drive."""

    slug: str
    drive_id: str
    title: str
    author: str

    @property
    def public_url(self) -> str:
        """Generate Google Drive direct download URL."""
        return f"https://drive.google.com/uc?export=download&id={self.drive_id}"


# Image assets from Google Drive
# These mirror the IDs used in react/scripts/fetch-images.mjs
IMAGES_CONFIG: List[ImageAsset] = [
    # Members
    ImageAsset("alfred", "1NLXEkoOz8CcVXXAFOMoCwttNoPVw7t35", "members"),
    ImageAsset("lemanu", "1vZxL4byBgKMExxKbakuZhEgQ2hsFDPVY", "members"),
    ImageAsset("levisax", "1kh42JDOOif795zfIgig1c3THcWXdvsYq", "members"),
    ImageAsset("rodrigo", "1EXP5Kh_RfxbQLrNVMUn7-Fygg1LrC7Xw", "members"),
    ImageAsset("sandy", "1EfbO0_BJL924CbnvjxfwbDaUj6Vo3uhp", "members"),
    ImageAsset("arthur", "10nWFvuwRtm_hR9LMtT5SmwRO5NCWey30", "members"),
    # Gallery
    ImageAsset("photo-1", "17NlhB47l-1RD9mlxM9hJpMwvSz1g8UEb", "gallery"),
    ImageAsset("photo-2", "1LmL-xTYYOU-jf1WVThT4N3Y9vLytwvWy", "gallery"),
]

# Audio assets - 15 second .wav clips from original songs
AUDIO_CONFIG: List[AudioAsset] = [
    # TODO: Populate with actual Google Drive IDs for 15s clips
    # AudioAsset("la_estacion", "DRIVE_ID_HERE", "La Estación", "Séptima Ola"),
    # AudioAsset("aguita_de_coco", "DRIVE_ID_HERE", "Agüita de Coco", "Séptima Ola"),
    # AudioAsset("salsa_callejera", "DRIVE_ID_HERE", "Salsa Callejera", "Séptima Ola"),
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
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# Codemie configuration
# All values are read from environment variables; these are just doc references.
# CODEMIE_BASE_URL      - Base URL of the Codemie instance
# CODEMIE_KEYCLOAK_URL  - Keycloak base URL
# CODEMIE_REALM         - Keycloak realm name
# CODEMIE_CLIENT_ID     - Keycloak client ID
# CODEMIE_CLIENT_SECRET - Keycloak client secret
# CODEMIE_ASSISTANT_ID  - UUID of the Codemie assistant to call

# Video generation settings
VIDEO_DURATION = 15  # seconds
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1080  # Square format for Instagram
VIDEO_FPS = 30
VIDEO_CODEC = "libx264"
AUDIO_CODEC = "aac"

# Facebook/Instagram API
FACEBOOK_API_VERSION = "v18.0"
FACEBOOK_BASE_URL = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}"
