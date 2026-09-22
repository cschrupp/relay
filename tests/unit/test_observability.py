import pytest

from relay_engine.observability import configure_logging, get_logger
from relay_engine.settings import RelaySettings


def test_logging_configuration_console(capsys: pytest.CaptureFixture[str]) -> None:
    settings = RelaySettings(environment="test", log_format="console", _env_file=None)
    configure_logging(settings)

    get_logger("test").info("relay_console_test", value=1)
    output = capsys.readouterr().out

    assert "relay_console_test" in output
    assert "value" in output


def test_logging_configuration_json(capsys: pytest.CaptureFixture[str]) -> None:
    settings = RelaySettings(environment="test", log_format="json", _env_file=None)
    configure_logging(settings)

    get_logger("test").info("relay_json_test", value=2)
    output = capsys.readouterr().out

    assert '"event": "relay_json_test"' in output
    assert '"value": 2' in output


def test_logging_configuration_idempotent(capsys: pytest.CaptureFixture[str]) -> None:
    settings = RelaySettings(environment="test", log_format="console", _env_file=None)
    configure_logging(settings)
    configure_logging(settings)

    get_logger("test").info("relay_once")
    output = capsys.readouterr().out

    assert output.count("relay_once") == 1
