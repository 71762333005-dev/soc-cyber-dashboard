import pytest


# Test 1: Flask app loads
def test_app_import():
    try:
        import app

        assert True
    except Exception as e:
        pytest.fail(f"App failed to load: {e}")


# Test 2: Flask home route (SOC dashboard UI)
def test_home_route():
    from app import app

    client = app.test_client()

    response = client.get("/")
    assert response.status_code == 200


# Test 3: Prediction module loads
def test_predict_import():
    try:
        import predict

        assert True
    except Exception as e:
        pytest.fail(f"Predict module error: {e}")


# Test 4: Dummy prediction test (SOC anomaly detection)
def test_dummy_prediction():
    from predict import AttackPredictor

    model = AttackPredictor()
    model.load_model()

    sample_input = [0.1, 0.2, 0.3, 0.4]

    result = model.predict(sample_input)

    assert result is not None
