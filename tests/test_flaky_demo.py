import random, pytest


@pytest.mark.flaky(reruns=5, reruns_delay=1)
def test_sometimes_fails():
    assert random.random() > 0.5
