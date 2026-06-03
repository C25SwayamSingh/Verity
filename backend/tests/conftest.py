import pytest

from app.core.rate_limit import get_rate_limiter
from app.db.session import init_db


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    get_rate_limiter().reset()
    init_db()
    yield
    get_rate_limiter().reset()
