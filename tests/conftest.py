import pytest
from quart import Quart


@pytest.fixture
def app():
    return Quart(__name__)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def dummy_order():
    def _dummy(custom=None):
        data = {
            "order_type": "sell",
            "platform": "pc",
            "region": "en",
            "platinum": 1,
            "quantity": 1,
            "item": {
                "id": "test",
                "tags": ["prime"],
            },
        }
        data.update(custom or {})
        return data

    return _dummy
