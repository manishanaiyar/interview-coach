def test_core_imports():
    """
    Tests that all core modules can be imported without syntax errors.
    """
    from src.core import generator, loader, processor, retriever
    assert True

def test_app_imports():
    """
    Tests that the UI and API apps can be imported.
    """
    from src.ui import app as ui_app
    from src.api import main as api_app
    assert True