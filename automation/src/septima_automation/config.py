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
    VideoAsset(
        "despertar_1", "1SqddSXFgL1Rr4yxMy2hccXFxHxAKua6L", "Despertar", "Septima Ola"
    ),
    VideoAsset("tqm_1", "1oyclVh9WyKYGNWJUgbUi3x9-Es7QKhd4", "Tqm", "Septima Ola"),
    VideoAsset(
        "ventana_1",
        "12bxqKGA5LUEMaPmwV2rL4PSZluQ377bV",
        "Desde Mi Ventana",
        "Séptima Ola",
    ),
    VideoAsset(
        "arenga_1", "1BIRUvp6Oi1SUs49wm8nLWzndsmz8hDZl", "Arenga", "Séptima Ola"
    ),
    VideoAsset("tqm_2", "1u_f6lXk2-IROknLaFb0QbdEjtqzK-eHR", "Tqm", "Séptima Ola"),
    VideoAsset("tqm_3", "16cTaAnPikBIroO9x3jW2Rfrrf442jjZ4", "Tqm", "Séptima Ola"),
    VideoAsset(
        "despertar_2", "1RHRS4tTd7xi-UHvTIjt_VCs5C4jXpVuR", "Despertar", "Séptima Ola"
    ),
    VideoAsset(
        "ventana_2",
        "1GGz1JwvDGv4AgVEBOsXeuQ-HtxlbhNBr",
        "Desde Mi Ventana",
        "Séptima Ola",
    ),
    VideoAsset(
        "arenga_2", "1HxGW-3QR_CScYUI9L00p-MbLfMRIRE1E", "Arenga", "Séptima Ola"
    ),
    VideoAsset("tqm_4", "1jZ0n8Eq2nPIwNrpZf5L_IWrhFQ2EUah0", "Tqm", "Séptima Ola"),
    VideoAsset(
        "ventana_3",
        "1M-hUx57GnEtrr7wH9Bmz8sKl657f0yDs",
        "Desde Mi Ventana",
        "Séptima Ola",
    ),
    VideoAsset(
        "despertar_3", "1rM2paJq9poq5Qo0Dm6tsIiYsqjeW-AfS", "Despertar", "Séptima Ola"
    ),
    VideoAsset(
        "4a644f1b-e88f-4e3a-99ab-814fe2fe7414.mp4",
        "1DJrOE7ommjpMHclUwydVEp4pfKNDdr9h",
        "Despertar",
        "Séptima Ola",
    ),
    VideoAsset(
        "12ef6afe-8a63-42aa-8783-5976b81f0256.mp4",
        "1Frv0RsIuxBNrbT8dJ78gPcpKIIT3py6R",
        "Despertar",
        "Séptima Ola",
    ),
    VideoAsset(
        "13a4637d-61d2-489b-8b5a-d0391f72a290.mp4",
        "1PhDboLBCfAZTxG0mJ2TW06yveOGuIS7z",
        "Tqm",
        "Séptima Ola",
    ),
    VideoAsset(
        "450b2956-7df6-4266-a165-2a99d3a86d92.mp4",
        "11p0fM-8aGc-zDFogBn-5rWSznX0VPKAJ",
        "Disco",
        "Séptima Ola",
    ),
    VideoAsset(
        "36843a3b-28dd-4ff0-96bb-b94fc71dedbc.mp4",
        "1kuKhHGAXOeg9JHb-oeF0KryjLjVs-JPx",
        "Desde Mi Ventana",
        "Séptima Ola",
    ),
    VideoAsset(
        "effe3f85-08a0-4d4c-9747-5ef564a740d1.mp4",
        "1BBnKCCi0PR6Wq9CsTuUr8aw-OvyFOzRs",
        "Arenga",
        "Séptima Ola",
    ),
    VideoAsset(
        "fa072729-2a3c-4255-8282-6ce7bda693eb.mp4",
        "1uiJpUFgINqhARDc36UrikdqnQ15mVZZi",
        "Desde Mi Ventana",
        "Séptima Ola",
    ),
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
    "#Mexico",
    "#MusicaIndependiente",
    "#Jazz",
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
# CODEMIE_TOKEN_URL     - Keycloak OAuth token endpoint
# CODEMIE_CLIENT_ID     - Keycloak client ID
# CODEMIE_CLIENT_SECRET - Keycloak client secret
# CODEMIE_MODEL         - Chat Completions model ID (default: gpt-4.1)

# Facebook/Instagram API
FACEBOOK_API_VERSION = "v25.0"
FACEBOOK_BASE_URL = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}"
