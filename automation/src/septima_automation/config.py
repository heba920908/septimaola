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
    VideoAsset("ed495a08-f3c1-4c42-9ae7-f32d03285a35.mp4", "1pl46qy4QX6BMJ6LaQUZPVVEk1Xm2KYPF", "Arenga", "Séptima Ola"),
    VideoAsset("dad8bce7-e22c-4777-9d28-0e2e5913d121.mp4", "1-pb5rOKj20vzI9zMRvBa4E0gzufD_Ulg", "Arenga", "Séptima Ola"),
    VideoAsset("31d1f8bd-49e9-49de-b964-1166fc6fec98.mp4", "1dXs7QKt2FjRDzKwOBXpuEvYuv5HdAZpd", "Arenga", "Séptima Ola"),
    VideoAsset("4137d9f2-b3f5-495d-86e0-18c7e9d6e823.mp4", "1Rat4SZfIwdFV4R-dRGKM9JvLtVSVYR6j", "Arenga", "Séptima Ola"),
    VideoAsset("271b7364-f996-4bd0-97f5-eeec73e7be69.mp4", "1D2mxr9b8sC8_yH-SwtyXOFeVpU1qNMCE", "Arenga", "Séptima Ola"),
    VideoAsset("5bffb6ce-acd9-4cc4-8c16-a3652dc2fd24.mp4", "1xH06S-0Qu5hiGs2VIU6Yh6meZfu4s18Y", "Arenga", "Séptima Ola"),
    VideoAsset("9c66d3db-51d3-4761-87fa-845a1128eb99.mp4", "1i0zhs7E8a7tgu6WbmvDJR9XzoBBZUFMp", "Desde mi ventana", "Séptima Ola"),
    VideoAsset("11fa5289-99fc-4018-a690-c02fce2ae635.mp4", "1MH_0HIvAwSpzVMCaOW2nZFWMOaPPeZ7W", "Desde mi ventana", "Séptima Ola"),
    VideoAsset("a8de8fd7-028c-4f6d-a461-fa70736a0875.mp4", "1u4Vy8c_EhVu6vf-UJEPK6d7eLid_MVZc", "Desde mi ventana", "Séptima Ola"),
    VideoAsset("c23f135f-8273-48a1-8be8-48b0b72175ff.mp4", "1zAuqwAm1WCiILjRankCfUZMs7r2LLSDL", "Desde mi ventana", "Séptima Ola"),
    VideoAsset("c54cf82b-3a47-4d0b-bf3b-049093cd5d46.mp4", "1SgwGJkSVDE5Tkye9S7vpZNdf9s0zHux7", "Desde mi ventana", "Séptima Ola"),
    VideoAsset("75475935-5e1d-4e03-8588-48057ee0b2e9.mp4", "1ooVYe0poZ5_ua4VB3S4XuR_3MHJH4BJC", "Desde mi ventana", "Séptima Ola"),
    VideoAsset("e53e874c-287b-4c01-839c-a30fa8456efd.mp4", "1XHb5igPS_Bt5_cTjWRM3__rkwcq7KICv", "Desde mi ventana", "Séptima Ola"),
    VideoAsset("f96b523c-5f4e-4f01-93ef-934c0ea117db.mp4", "1fUNfSEgjx4P-SXez2Ywe4_DZ3DKR7IBv", "Desde mi ventana", "Séptima Ola"),
    VideoAsset("fd8c2c1c-0601-4263-8866-bb370bd2d69c.mp4", "1uPNmHViYyMb4EVX6saYZFfeao_IDlb6N", "Desde mi ventana", "Séptima Ola"),
    VideoAsset("b0903cbf-2d8a-4e2a-a2f5-6b91edc87b44.mp4", "1_KzARQn7l0legZ-SJFSQ6zsP4VhRsFZq", "Desde mi ventana", "Séptima Ola"),
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
