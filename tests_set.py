# test set for plugin testing
# from IPython import embed
import ipdb
import pytest

class Dut(object):
    'fake a device under test'

    _allowed = ('a', 'b', 'c')

    def __init__(self, mode=None):
        self._mode = mode

    def get_mode(self):
        return self._mode

    def set_mode(self, val):
        self._mode = val

    def check_mode(self):
        assert self._mode in self._allowed

# fixtures
@pytest.fixture
def dut(request):
    return Dut('c')

@pytest.yield_fixture
def mode_a(dut):
    orig_mode = dut.get_mode()
    dut.set_mode('a')
    yield dut
    dut.set_mode(orig_mode)

@pytest.yield_fixture
def mode_b(dut):
    orig_mode = dut.get_mode()
    dut.set_mode('b')
    yield dut
    dut.set_mode(orig_mode)

@pytest.mark.usefixtures("mode_a", "mode_b")
def test_mode():
    assert True
