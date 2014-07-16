import pytest
import ipdb

def pytest_addoption(parser):
    parser.addoption("--i", "--interactive", action="store_true",
            help="enable iteractive selection of tests after the collection")


def collect_modify_items(session, config, items):
    if not config.option.interactive:
        return
    import ipdb
    ipdb.set_trace()
