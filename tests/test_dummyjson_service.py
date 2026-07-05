from src.app.services.dummyjson import calculate_priority, calculate_status


def test_calculate_status():
    assert calculate_status(True) == "closed"
    assert calculate_status(False) == "open"


def test_calculate_priority():
    assert calculate_priority(3) == "low"
    assert calculate_priority(4) == "medium"
    assert calculate_priority(5) == "high"