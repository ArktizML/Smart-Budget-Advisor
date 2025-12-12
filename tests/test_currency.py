from app.currency import convert

def test_convert_pln_to_eur():
    rates = {"EUR": 0.25, "USD": 0.30}
    result = convert(100, "PLN", "EUR", rates)
    assert result == 25

def test_convert_same_currency():
    rates = {"PLN": 1}
    result = convert(50, "PLN", "PLN", rates)
    assert result == 50

def test_convert_missing_rate():
    rates = {}
    result = convert(100, "PLN", "EUR", rates)
    assert result == 100