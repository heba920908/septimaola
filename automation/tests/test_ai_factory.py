"""Tests for the AI provider factory and constructor guards."""

import pytest

from septima_automation.ai.factory import create_provider
from septima_automation.ai.deepseek import DeepseekClient
from septima_automation.ai.codemie import CodemieClient


class TestCreateProvider:
    """Test create_provider() routing and fallback logic."""

    def test_factory_returns_deepseek_by_default(self, monkeypatch):
        """No arg and no env var → returns DeepseekClient."""
        monkeypatch.delenv("AI_PROVIDER", raising=False)
        monkeypatch.setenv("DEEPSEEK_API_KEY", "fake-key")
        provider = create_provider()
        assert isinstance(provider, DeepseekClient)

    def test_factory_env_var_selects_deepseek(self, monkeypatch):
        """AI_PROVIDER=deepseek env var → DeepseekClient."""
        monkeypatch.setenv("AI_PROVIDER", "deepseek")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "fake-key")
        provider = create_provider()
        assert isinstance(provider, DeepseekClient)

    def test_factory_env_var_selects_codemie(self, monkeypatch):
        """AI_PROVIDER=codemie env var → CodemieClient."""
        monkeypatch.setenv("AI_PROVIDER", "codemie")
        monkeypatch.setenv("CODEMIE_BASE_URL", "https://codemie.example.com")
        monkeypatch.setenv("CODEMIE_KEYCLOAK_URL", "https://keycloak.example.com")
        monkeypatch.setenv("CODEMIE_REALM", "test-realm")
        monkeypatch.setenv("CODEMIE_CLIENT_ID", "test-client")
        monkeypatch.setenv("CODEMIE_CLIENT_SECRET", "test-secret")
        monkeypatch.setenv("CODEMIE_ASSISTANT_ID", "test-assistant-uuid")
        provider = create_provider()
        assert isinstance(provider, CodemieClient)

    def test_factory_explicit_name_overrides_env(self, monkeypatch):
        """Explicit name arg wins over AI_PROVIDER env var."""
        monkeypatch.setenv("AI_PROVIDER", "codemie")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "fake-key")
        provider = create_provider(name="deepseek")
        assert isinstance(provider, DeepseekClient)

    def test_factory_raises_on_unknown_provider(self, monkeypatch):
        """Unknown provider name → ValueError with helpful message."""
        monkeypatch.delenv("AI_PROVIDER", raising=False)
        with pytest.raises(ValueError, match="Unknown AI provider"):
            create_provider(name="openai")

    def test_factory_raises_on_unknown_provider_via_env(self, monkeypatch):
        """Unknown provider from env var → ValueError."""
        monkeypatch.setenv("AI_PROVIDER", "not-a-real-provider")
        with pytest.raises(ValueError, match="Unknown AI provider"):
            create_provider()


class TestDeepseekClientConstructor:
    """Test DeepseekClient constructor credential guard."""

    def test_raises_without_api_key(self, monkeypatch):
        """Constructor raises ValueError when DEEPSEEK_API_KEY is absent."""
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        with pytest.raises(ValueError, match="DEEPSEEK_API_KEY"):
            DeepseekClient()

    def test_accepts_api_key_from_env(self, monkeypatch):
        """Constructor succeeds when DEEPSEEK_API_KEY is set in env."""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-key")
        client = DeepseekClient()
        assert client.api_key == "sk-test-key"

    def test_accepts_api_key_as_argument(self, monkeypatch):
        """Constructor arg takes precedence over env var."""
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        client = DeepseekClient(api_key="direct-key")
        assert client.api_key == "direct-key"


class TestCodemieClientConstructor:
    """Test CodemieClient constructor credential guards."""

    _FULL_CREDS = {
        "base_url": "https://codemie.example.com",
        "keycloak_url": "https://keycloak.example.com",
        "realm": "test-realm",
        "client_id": "test-client",
        "client_secret": "test-secret",
        "assistant_id": "test-uuid",
    }

    def _clear_codemie_env(self, monkeypatch):
        for var in [
            "CODEMIE_BASE_URL",
            "CODEMIE_KEYCLOAK_URL",
            "CODEMIE_REALM",
            "CODEMIE_CLIENT_ID",
            "CODEMIE_CLIENT_SECRET",
            "CODEMIE_ASSISTANT_ID",
        ]:
            monkeypatch.delenv(var, raising=False)

    def test_raises_when_all_credentials_missing(self, monkeypatch):
        """Constructor raises ValueError listing all missing vars."""
        self._clear_codemie_env(monkeypatch)
        with pytest.raises(ValueError, match="Missing required Codemie credentials"):
            CodemieClient()

    def test_raises_when_single_credential_missing(self, monkeypatch):
        """Constructor raises ValueError when just one var is absent."""
        self._clear_codemie_env(monkeypatch)
        creds = dict(self._FULL_CREDS)
        del creds["assistant_id"]
        with pytest.raises(ValueError, match="CODEMIE_ASSISTANT_ID"):
            CodemieClient(**creds)

    def test_succeeds_with_all_credentials_as_args(self, monkeypatch):
        """Constructor succeeds when all creds are passed as arguments."""
        self._clear_codemie_env(monkeypatch)
        client = CodemieClient(**self._FULL_CREDS)
        assert client.base_url == "https://codemie.example.com"
        assert client.realm == "test-realm"
        assert client.assistant_id == "test-uuid"

    def test_trailing_slash_stripped_from_base_url(self, monkeypatch):
        """Trailing slash is removed from base_url and keycloak_url."""
        self._clear_codemie_env(monkeypatch)
        creds = dict(self._FULL_CREDS)
        creds["base_url"] = "https://codemie.example.com/"
        creds["keycloak_url"] = "https://keycloak.example.com/"
        client = CodemieClient(**creds)
        assert not client.base_url.endswith("/")
        assert not client.keycloak_url.endswith("/")
