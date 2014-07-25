import sys
import _pytest
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
    if not config.option.interactive:
        return

    # prep and embed ipython
    from IPython.terminal.embed import InteractiveShellEmbed
    ipshell = InteractiveShellEmbed(banner1='Entering IPython workspace...',
                                  exit_msg='Leaving interpreter starting pytest run')

    # build a tree of test items
    tt = TestTree(items, ipshell)
    ipshell("Welcome to pytest-interactive, the ipython-pytest bonanza!")


_root_id = '.'
Package = namedtuple('Package', 'name path')
Directory = namedtuple('Directory', 'name path')


# XXX consider adding in a cache
# maybe this could be implemented more elegantly as a generator?
def get_path(nodes, path=(), _node_cache={}):
    '''return all parent objs of this node up to the root/session'''
    node = nodes[0]  # the most recently prefixed node
    newnodes = ()
    try:
        name = node._obj.__name__
        print("__name__ is {}".format(name))
        if '.' in name and isinstance(node, _pytest.python.Module):  # packaged module
            pkgname = node._obj.__package__
            prefix = tuple(name.split('.'))
            lpath = node.fspath
            for level in reversed(prefix[:-1]):
                lpath = lpath.join('../')
                newnodes = (Package(level, lpath),) + newnodes
        else:
            prefix = (name,)  # pack
    except AttributeError as ae:  # when either Instance or non-packaged module
        if isinstance(node, _pytest.python.Instance):
            prefix = ('Instance',)  # don't bother with the instance node/step
        elif isinstance(node, _pytest.python.Module):
            print("ERROR!!!?")
        else :  # should never get here
            print('Error wtf detected!? -> {}'.format(node))
            prefix = ('wtf?',)

    newnodes = (node.parent,) + newnodes
    # edge case (the root/session)
    if node.parent.nodeid == _root_id:
        return newnodes + nodes, (_root_id,) + prefix + path
    # normal case
    if node.parent:
        return get_path(newnodes + nodes, path=prefix + path)
    else:
        raise ValueError("node '{}' has no parent?!".format(node))


# borrowed from:
# http://stackoverflow.com/questions/4126348/how-do-i-rewrite-this-function-to-implement-ordereddict/4127426#4127426
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


class TestTree(object):
    def __init__(self, funcitems, ipshell):
        self._shell = ipshell
        self._funcitems = funcitems  # never modify this
        self._path2funcs = OrderedDefaultdict(set)
        self._path2children = defaultdict(set)
        self._nodes = {}
        for item in funcitems:
            print(item)
            nodes, path = get_path((item,))
            for i, (key, node) in enumerate(zip(path, nodes), 1):
                loc = path[:i]
                child = path[:i+1]
                # print(loc)
                self._path2funcs[loc].add(item)
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
        return dir(self._root) + dir(self.__class__)

    def _runall(self, path):
        funcitems = self._path2funcs[path]
        self._funcitems[:] = funcitems
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
                return self._new(attr)
            except TypeError:
                raise ae

    def _get_node(self):
        return self._tree._nodes[self._path]

    node = property(_get_node)

    def _new(self, key):
        'return a new node'
        if key is 'parent':
            path = self._path[:-1]
        else:
            path = self._path + (key,)
        return type(self)(self._tree, path)

    def __call__(self):
        'Run all tests under this node'
        return self._tree._runall(self._path)
