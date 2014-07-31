import sys
import _pytest
import pytest
import IPython
import types
from collections import OrderedDict, namedtuple, defaultdict

def pytest_addoption(parser):
    parser.addoption("--i", "--interactive", action="store_true",
            dest='interactive',
            help="enable iteractive selection of tests after collection")


def pytest_keyboard_interrupt(excinfo):
    'enter the debugger on keyboard interrupt'
    pytest.set_trace()


def pytest_collection_modifyitems(session, config, items):
    """called after collection has been performed, may filter or re-order
    the items in-place."""
    if not (config.option.interactive and items) or config.option.collectonly:
        return

    # prep and embed ipython
    from IPython.terminal.embed import InteractiveShellEmbed
    ipshell = InteractiveShellEmbed(banner1='Entering IPython workspace...',
                                  exit_msg='Exiting IPython, beginning pytest run...')

    # build a tree of test items
    tt = TestTree(items, ipshell)
    ipshell("Welcome to pytest-interactive.\nPlease explore the test "
            "tree using tt.<tab> to select and run a subset of tests from the "
            "collection tree.\n"
            "When finshed navigating to a test node, simply call it to have "
            "pytest invoke all tests under that node.")

    # don't run any tests by default
    if not tt._selected and not config.option.collectonly:
        items[:] = []


# borrowed from:
# http://stackoverflow.com/questions/4126348/
# how-do-i-rewrite-this-function-to-implement-ordereddict/4127426#4127426
class OrderedDefaultdict(OrderedDict):

    def __init__(self, *args, **kwargs):
        if not args:
            self.default_factory = None
        else:
            if not (args[0] is None or callable(args[0])):
                raise TypeError('first argument must be callable or None')
            self.default_factory = args[0]
        args = args[1:]
        super(OrderedDefaultdict, self).__init__(*args, **kwargs)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = default = self.default_factory()
        return default

    def __reduce__(self):  # optional, for pickle support
        args = (self.default_factory,) if self.default_factory else ()
        return self.__class__, args, None, None, self.iteritems()


_root_id = '.'
Package = namedtuple('Package', 'name path node')
# Directory = namedtuple('Directory', 'name path node')
# ParametrizedFunc = namedtuple('ParametrizedFunc', 'name count')

class ParametrizedFunc(object):
    def __init__(self, name, instances):
        if not isinstance(instances, list):
            instances = [instances]
        self._instances = instances

    def __dir__(self):
        attrs = sorted(set(dir(type(self)) + self.__dict__.keys()))
        return self._instances + attrs


# XXX consider adding in a cache
# maybe this could be implemented more elegantly as a generator?
# XXX consider leveraging node.listchain()
# here instead of recursing..
def build_path(nodes, path=(), _node_cache={}):
    '''return all parent objs of this node up to the root/session'''
    node = nodes[0]  # the most recently prefixed node
    newnodes = ()
    try:
        name = node._obj.__name__
        # print("__name__ is {}".format(name))
        if '.' in name and isinstance(node, _pytest.python.Module):  # packaged module
            pkgname = node._obj.__package__
            prefix = tuple(name.split('.'))
            lpath = node.fspath
            for level in reversed(prefix[:-1]):
                lpath = lpath.join('../')
                newnodes = (Package(level, lpath, node),) + newnodes
        elif isinstance(node, _pytest.python.Function):
            # print("function name is {}".format(name))
            name = node.name
            if '[' in name:
                name = name.split('[')[0]
            # else:
            #     name = node._obj.__name__
            newnodes = (ParametrizedFunc(name, node),) + newnodes
            prefix = (name,)
        else:
            prefix = (name,)  # pack
    except AttributeError as ae:  # when either Instance or non-packaged module
        if isinstance(node, _pytest.python.Instance):
            prefix = ('Instance',)  # don't bother with the instance node/step
        else :  # should never get here
            raise ae

    newnodes = (node.parent,) + newnodes
    # edge case (the root/session)
    if node.parent.nodeid == _root_id:
        return newnodes + nodes, (_root_id,) + prefix + path
    # normal case
    if node.parent:
        return build_path(newnodes + nodes, path=prefix + path)
    else:
        raise ValueError("node '{}' has no parent?!".format(node))


class TestTree(object):
    def __init__(self, funcitems, ipshell):
        self._shell = ipshell
        self._funcitems = funcitems  # never modify this
        self._path2items = OrderedDefaultdict(set)
        self._path2children = defaultdict(set)
        self._selected = False
        self._nodes = {}
        self._cache = {}
        for item in funcitems:
            # print(item)
            nodes, path = build_path((item,), _node_cache=self._nodes)
            for i, (key, node) in enumerate(zip(path, nodes), 1):
                loc = path[:i]
                child = path[:i+1]
                # print(loc)
                self._path2items[loc].add(item)
                if loc != child:
                    self._path2children[loc].add(child)
                    # print(child)
                if loc not in self._nodes:
                    self._nodes[loc] = node
        self._root = Node(self, (_root_id,))#, funcitems)

    def _get_children(self, path):
        'return the children for a node'
        return self._path2children[path]

    def __getattr__(self, key):
        try:
            object.__getattribute__(self, key)
        except AttributeError as ae:
            try:
                return getattr(self._root, key)
            except AttributeError:
                raise ae

    def __dir__(self, key=None):
        attrs = sorted(set(dir(type(self)) + self.__dict__.keys()))
        return dir(self._root) + attrs

    def _runall(self, path):
        # XXX can this selection remain ordered to avoid
        # traversing the list again?...imagined speed gain in my head?
        items = self._path2items[path]
        self._funcitems[:] = [f for f in self._funcitems if f in items]
        if not self._selected:
            self._selected = True
        self._shell.exit()


class Node(object):
    def __init__(self, tree, path):
        self._tree = tree
        self._path = path
        self._len = len(path)

    def __dir__(self):
        children = self._tree._get_children(self._path)
        return sorted([key[self._len] for key in children])

    def __getattr__(self, attr):
        try:
            object.__getattribute__(self, attr)
        except AttributeError as ae:
            try:
                self._get_node(self._path + (attr,))
                return self._sub(attr)
            except TypeError:
                raise ae
            except KeyError:
                raise AttributeError("sub-node '{}' can not be found".format(attr))

    def _get_node(self, path=None):
        if not path:
            path = self._path
        return self._tree._nodes[path]

    _node = property(_get_node)

    def _get_items(self):
        return self._tree._path2items[self._path]

    _items = property(_get_items)

    def _sub(self, key):
        'return a (new/cached) sub node'
        if key is 'parent':
            path = self._path[:-1]
        else:
            path = self._path + (key,)
        return self._tree._cache.setdefault(path, type(self)(self._tree, path))

    def __call__(self):
        'Run all tests under this node'
        return self._tree._runall(self._path)
