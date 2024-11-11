def pytest_collection_modifyitems(session, config, items):
    # Avoid executing tests when executing `--flake8` flag (pytest-flake8)
    try:
        from pytest_flake8 import Flake8Item

        if config.getoption("--flake8"):
            items[:] = [item for item in items if isinstance(item, Flake8Item)]
    except ImportError:
        pass
