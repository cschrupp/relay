import relay_engine


def test_package_imports() -> None:
    assert relay_engine.__version__ == "0.1.0.dev0"
