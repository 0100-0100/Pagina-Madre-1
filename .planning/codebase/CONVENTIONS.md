# Coding Conventions

**Analysis Date:** 2026-01-16

## Naming Patterns

**Files:**
- Python modules: `snake_case.py` (e.g., `settings.py`, `urls.py`, `wsgi.py`, `asgi.py`)
- Management script: `manage.py` at project level
- Package markers: `__init__.py` for Python packages

**Functions:**
- `snake_case` following Python PEP 8 standards
- Docstrings use triple-quoted strings (e.g., `"""Run administrative tasks."""`)

**Variables:**
- `UPPERCASE_WITH_UNDERSCORES` for constants and settings (e.g., `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`)
- `snake_case` for standard variables (e.g., `os.environ.setdefault`)
- `CapitalizedWords` for class names following PEP 8

**Types:**
- Django follows standard Python typing conventions
- Model field types use Django's built-in field classes

## Code Style

**Formatting:**
- Standard Python PEP 8 formatting
- 4 spaces for indentation
- Single quotes for strings in imports (`from django.contrib import admin`)
- Triple double-quotes for docstrings (`"""..."""`)
- No explicit formatter configuration detected (no `.prettierrc`, `.black`, or similar)

**Linting:**
- No explicit linter configuration detected (no `.flake8`, `.pylintrc`, `.ruff.toml`)
- Django project relies on standard Python conventions

## Import Organization

**Order:**
1. Standard library imports (`import os`, `import sys`, `from pathlib import Path`)
2. Third-party imports (`from django.contrib import admin`, `from django.urls import path`)
3. Local application imports (not yet present in scaffold)

**Path Aliases:**
- No custom path aliases detected
- Django settings module: `___.settings`
- Standard Django imports from `django.core`, `django.contrib`, etc.

## Error Handling

**Patterns:**
- Explicit exception chaining with `from exc` syntax:
```python
except ImportError as exc:
    raise ImportError(
        "Couldn't import Django. Are you sure it's installed and "
        "available on your PYTHONPATH environment variable? Did you "
        "forget to activate a virtual environment?"
    ) from exc
```
- Descriptive error messages for common issues
- Exception types specified explicitly (`ImportError`)

## Logging

**Framework:** Not explicitly configured (Django default logging)

**Patterns:**
- No custom logging configuration in `___/___/settings.py`
- Django uses built-in logging framework
- Standard output for errors via exception messages

## Comments

**When to Comment:**
- Module-level docstrings for all Python files explaining purpose
- Function docstrings for entry points (e.g., `def main():`)
- Inline comments for configuration sections in `settings.py`
- References to Django documentation URLs for settings explanations

**JSDoc/TSDoc:**
- Not applicable (Python project)
- Uses Python docstrings with triple-quoted strings
- Format: `"""Brief description on first line."""`

## Function Design

**Size:** Functions are concise and single-purpose

**Parameters:**
- Minimal parameters for entry point functions
- Environment variables used for configuration (`os.environ.setdefault`)

**Return Values:**
- Functions without explicit return values follow Python conventions
- Entry points call framework methods without explicit returns

## Module Design

**Exports:**
- Django standard structure with explicit URL patterns (`urlpatterns = [...]`)
- Configuration as module-level variables (all Django settings)
- ASGI/WSGI applications exported as `application` variable

**Barrel Files:**
- Not applicable (Python uses `__init__.py` for package initialization)
- Empty `__init__.py` files mark directories as Python packages

## Django-Specific Conventions

**Settings Structure:**
- Constants in UPPERCASE (e.g., `BASE_DIR`, `SECRET_KEY`, `DEBUG`)
- Lists for apps and middleware (e.g., `INSTALLED_APPS`, `MIDDLEWARE`)
- Dictionary configuration for databases, templates, etc.
- Comments with Django documentation URLs for reference

**Project Structure:**
- Project name: `___` (placeholder name, should be renamed)
- Settings module reference: `___.settings`
- URL configuration: `___.urls`
- WSGI/ASGI applications: `___.wsgi.application`, `___.asgi.application`

**String Formatting:**
- f-strings not observed in current code
- String concatenation in error messages using explicit strings

---

*Convention analysis: 2026-01-16*
