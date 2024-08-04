import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    return db

@pytest.fixture(autouse=True)
def setup_context():
    pytest.context = {}
