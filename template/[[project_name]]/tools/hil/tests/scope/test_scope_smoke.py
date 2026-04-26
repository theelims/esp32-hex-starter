import pytest


@pytest.mark.hil
def test_scope_identifies(scope):
    idn = scope.scope.query("*IDN?")
    assert "SDS1104X-E" in idn
