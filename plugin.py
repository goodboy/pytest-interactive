import pytest
import ipdb

def pytest_addoption(parser):
    parser.addoption("-i", action="store_true",
            help="enable iteractive selection of tests")
