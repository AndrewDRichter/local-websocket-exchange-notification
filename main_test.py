from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_gas_price():
    response = client.get("/gas-price/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}

def test_gas_price():
    response = client.get("/gas-price/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}

def test_exchange_values():
    response = client.get("/exchange-values/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}

def test_soybean_cost():
    response = client.get("/soybean-cost/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}
