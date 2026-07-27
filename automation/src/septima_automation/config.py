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
    VideoAsset("despertar_1", "1SqddSXFgL1Rr4yxMy2hccXFxHxAKua6L", "Despertar", "Septima Ola"),
    VideoAsset("tqm_1", "1oyclVh9WyKYGNWJUgbUi3x9-Es7QKhd4", "Tqm", "Septima Ola"),
    VideoAsset("ventana_1", "12bxqKGA5LUEMaPmwV2rL4PSZluQ377bV", "Desde Mi Ventana", "Séptima Ola"),
    VideoAsset("arenga_1", "1BIRUvp6Oi1SUs49wm8nLWzndsmz8hDZl", "Arenga", "Séptima Ola"),
    VideoAsset("tqm_2", "1u_f6lXk2-IROknLaFb0QbdEjtqzK-eHR", "Tqm", "Séptima Ola"),
    VideoAsset("tqm_3", "16cTaAnPikBIroO9x3jW2Rfrrf442jjZ4", "Tqm", "Séptima Ola"),
    VideoAsset("despertar_2", "1RHRS4tTd7xi-UHvTIjt_VCs5C4jXpVuR", "Despertar", "Séptima Ola"),
    VideoAsset("ventana_2", "1GGz1JwvDGv4AgVEBOsXeuQ-HtxlbhNBr", "Desde Mi Ventana", "Séptima Ola"),
    VideoAsset("arenga_2", "1HxGW-3QR_CScYUI9L00p-MbLfMRIRE1E", "Arenga", "Séptima Ola"),
    VideoAsset("tqm_4", "1jZ0n8Eq2nPIwNrpZf5L_IWrhFQ2EUah0", "Tqm", "Séptima Ola"),
    VideoAsset("ventana_3", "1M-hUx57GnEtrr7wH9Bmz8sKl657f0yDs", "Desde Mi Ventana", "Séptima Ola"),
    VideoAsset("despertar_3", "1rM2paJq9poq5Qo0Dm6tsIiYsqjeW-AfS", "Despertar", "Séptima Ola"),
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
FACEBOOK_API_VERSION = "v25.0"
FACEBOOK_BASE_URL = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}"
