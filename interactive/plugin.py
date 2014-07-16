import pytest
import ipdb

def pytest_addoption(parser):
    parser.addoption("--i", "--interactive", action="store_true",
            dest='interactive',
            help="enable iteractive selection of tests after collection")


def pytest_collection_modifyitems(session, config, items):
     """ called after collection has been performed, may filter or re-order
     the items in-place."""
    if not config.option.interactive:
        return
    ipdb.set_trace()
