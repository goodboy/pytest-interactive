# test set for plugin testing
# from IPython import embed
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


@pytest.yield_fixture(params=('a', 'b', 'c'))
def mode(request, dut):
    orig_mode = dut.get_mode()
    dut.set_mode(request.param)
    yield dut
    dut.set_mode(orig_mode)


@pytest.yield_fixture(params=['dog', 'cat', 'mouse'])
def inputs(request):
    yield request.param


def test_modes(mode):
    assert mode.check_mode()


def test_inputs(inputs):
    assert inputs < 2


class TestBoth(object):
    def test_m(self, mode, inputs):
        assert mode.check_mode()
        assert inputs < 2
