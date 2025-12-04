import pytest
import importlib
from pathlib import Path
from datetime import datetime
from config import settings
from modules.base import FetchResult

# Dynamically find all modules in 'modules' and 'dev' directories
def get_modules():
    modules = []
    for folder in ["modules", "dev"]:
        path = settings.BASE_DIR / folder
        if path.exists():
            for f in path.iterdir():
                if f.suffix == ".py" and not f.name.startswith("_") and f.name != "base.py":
                    modules.append(f"{folder}.{f.stem}")
    return modules

MODULES_TO_TEST = get_modules()

@pytest.mark.parametrize("module_name", MODULES_TO_TEST)
def test_module_structure(module_name):
    """Test that the module has a fetch function."""
    mod = importlib.import_module(module_name)
    assert hasattr(mod, "fetch"), f"Module {module_name} must have a 'fetch' function"
    assert callable(mod.fetch), f"Module {module_name}.fetch must be callable"

@pytest.mark.parametrize("module_name", MODULES_TO_TEST)
def test_module_fetch_contract(module_name):
    """Test that the module's fetch function returns a valid result."""
    mod = importlib.import_module(module_name)
    
    # Use a past date that is likely to have data, or a weekend/holiday to test handling
    # For now, we use today or a fixed recent date. 
    # Ideally, modules should support a 'dry_run' or 'test_mode' but for now we call it directly.
    # WARNING: This makes real network requests.
    
    test_date = "2025-11-28" # A known weekday from the user's context
    
    try:
        result = mod.fetch(test_date)
    except Exception as e:
        pytest.fail(f"Module {module_name} raised exception during fetch: {e}")

    # Validate against Pydantic model
    # If the module returns a dict, we try to parse it
    if isinstance(result, dict):
        try:
            fetch_result = FetchResult(**result)
        except Exception as e:
            pytest.fail(f"Module {module_name} returned invalid data structure: {e}")
    else:
        pytest.fail(f"Module {module_name} must return a dict (or FetchResult model)")

    assert fetch_result.date == test_date
