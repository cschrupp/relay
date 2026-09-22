import pytest
from pydantic import ValidationError

from relay_engine.settings import RelaySettings


def test_settings_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "RELAY_ENVIRONMENT",
        "RELAY_SERVICE_NAME",
        "RELAY_LOG_LEVEL",
        "RELAY_LOG_FORMAT",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = RelaySettings(_env_file=None)

    assert settings.environment == "local"
    assert settings.service_name == "relay-engine"
    assert settings.log_level == "INFO"
    assert settings.log_format == "console"


def test_settings_environment_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RELAY_ENVIRONMENT", "test")
    monkeypatch.setenv("RELAY_SERVICE_NAME", "relay-test")
    monkeypatch.setenv("RELAY_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("RELAY_LOG_FORMAT", "json")

    settings = RelaySettings(_env_file=None)

    assert settings.environment == "test"
    assert settings.service_name == "relay-test"
    assert settings.log_level == "DEBUG"
    assert settings.log_format == "json"


def test_invalid_settings_rejected() -> None:
    with pytest.raises(ValidationError):
        RelaySettings(environment="unknown", _env_file=None)  # type: ignore[arg-type]
