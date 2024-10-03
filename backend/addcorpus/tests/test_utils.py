from addcorpus.utils import is_date


def test_is_date():
    assert is_date('2024-01-01')
    assert not is_date(None)
    assert not is_date(5)
    assert not is_date('01-01-2024')
