# Testing Patterns

**Analysis Date:** 2026-01-16

## Test Framework

**Runner:**
- Django's built-in test framework (extends Python's `unittest`)
- Version: Django 6.0.1

**Assertion Library:**
- Python's built-in `unittest` assertions
- Django test case classes (`django.test.TestCase`, `django.test.SimpleTestCase`)

**Run Commands:**
```bash
python ___/manage.py test              # Run all tests
python ___/manage.py test --keepdb     # Run with database persistence
python ___/manage.py test --parallel   # Run tests in parallel
python ___/manage.py test app_name     # Run specific app tests
python ___/manage.py test --verbosity=2 # Detailed output
```

## Test File Organization

**Location:**
- Co-located with application code
- Standard Django pattern: `tests.py` in each app directory, or `tests/` package

**Naming:**
- `tests.py` for simple test modules
- `tests/__init__.py` with `test_*.py` files for complex test suites
- Test methods: `test_<description>` following Python unittest conventions

**Structure:**
```
___/
├── app_name/
│   ├── models.py
│   ├── views.py
│   └── tests.py           # or tests/ directory
└── manage.py
```

## Test Structure

**Suite Organization:**
```python
from django.test import TestCase

class ModelNameTestCase(TestCase):
    """Test suite for ModelName model."""

    def setUp(self):
        """Set up test data before each test method."""
        # Create test objects
        pass

    def test_specific_behavior(self):
        """Test specific functionality."""
        # Arrange
        # Act
        # Assert
        self.assertEqual(expected, actual)

    def tearDown(self):
        """Clean up after each test method."""
        pass
```

**Patterns:**
- Class-based test organization using `TestCase` subclasses
- `setUp()` for test data initialization
- `tearDown()` for cleanup (optional, Django handles DB cleanup)
- Descriptive test method names with `test_` prefix
- Docstrings for test classes and methods

## Mocking

**Framework:** Python's built-in `unittest.mock`

**Patterns:**
```python
from unittest.mock import patch, MagicMock

class ViewTestCase(TestCase):
    @patch('app.module.external_service')
    def test_with_mock(self, mock_service):
        """Test with mocked external service."""
        mock_service.return_value = expected_value
        # Test code
```

**What to Mock:**
- External API calls
- Third-party service integrations
- File system operations
- Email sending
- Time-dependent functions

**What NOT to Mock:**
- Django ORM queries (use test database)
- Django views (use test client)
- Internal business logic

## Fixtures and Factories

**Test Data:**
```python
# Using Django fixtures (JSON/YAML files)
class MyTestCase(TestCase):
    fixtures = ['initial_data.json']

# Using factory pattern in setUp
class MyTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
```

**Location:**
- Fixture files: `app_name/fixtures/` directory
- Factory methods: In test class `setUp()` or separate `factories.py`

## Coverage

**Requirements:** Not enforced (no configuration detected)

**View Coverage:**
```bash
coverage run --source='.' ___/manage.py test
coverage report
coverage html                # Generate HTML report
```

## Test Types

**Unit Tests:**
- Test individual models, methods, utilities
- Use `django.test.SimpleTestCase` for non-database tests
- Use `django.test.TestCase` for database-dependent tests

**Integration Tests:**
- Use Django test client for view testing
- Test complete request/response cycles
- Example:
```python
from django.test import Client, TestCase

class ViewIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_view_response(self):
        response = self.client.get('/url/')
        self.assertEqual(response.status_code, 200)
```

**E2E Tests:**
- Django's `LiveServerTestCase` for Selenium integration
- Not currently configured in this project

## Common Patterns

**Async Testing:**
```python
from django.test import TestCase

class AsyncViewTest(TestCase):
    async def test_async_view(self):
        """Test asynchronous view functionality."""
        response = await self.async_client.get('/async-url/')
        self.assertEqual(response.status_code, 200)
```

**Error Testing:**
```python
class ErrorTestCase(TestCase):
    def test_raises_exception(self):
        """Test that specific exception is raised."""
        with self.assertRaises(ValueError):
            # Code that should raise ValueError
            function_that_raises()

    def test_error_message(self):
        """Test exception message content."""
        with self.assertRaisesMessage(ValueError, 'Expected error'):
            function_that_raises()
```

## Django Test Database

**Configuration:**
- Test database created automatically (prefix: `test_`)
- Uses SQLite by default: `test_db.sqlite3`
- Migrations run automatically before tests
- Database destroyed after test run (unless `--keepdb` used)

**Transaction Handling:**
- Each test runs in a transaction (auto-rollback)
- `TransactionTestCase` for tests requiring commit/rollback
- `TestCase` for standard isolated tests

## Test Client Patterns

**HTTP Testing:**
```python
def test_get_request(self):
    response = self.client.get('/path/')
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Expected content')

def test_post_request(self):
    response = self.client.post('/path/', {'key': 'value'})
    self.assertRedirects(response, '/success/')
```

**Authentication:**
```python
def test_authenticated_view(self):
    self.client.login(username='user', password='pass')
    response = self.client.get('/protected/')
    self.assertEqual(response.status_code, 200)
```

---

*Testing analysis: 2026-01-16*
