import _pytest
import IPython
from collections import OrderedDict, namedtuple, defaultdict

def pytest_addoption(parser):
    parser.addoption("--i", "--interactive", action="store_true",
            dest='interactive',
            help="enable iteractive selection of tests after collection")


def pytest_keyboard_interrupt(excinfo):
    'called for keyboard interrupt'
    pass


def pytest_collection_modifyitems(session, config, items):
    """called after collection has been performed, may filter or re-order
    the items in-place."""
    if not config.option.interactive:
        return

    root = TestTree(items)
    # build a tree of test items
    IPython.embed()

_root_id = '.'

def get_modpath(nodes, path=()):
    '''return the eldest parent of this node
    a child of the root/session'''
    node = [0]
    try:
        step = (node._obj.__name__,)
    except AttributeError:
        step = ()  # don't bother with the instance node/step
    if node.parent.nodeid == _root_id:  # the root/session
        return (node.parent,) + nodes, (_root_id,) + step + path
    if node.parent:
        return get_modpath((node.parent,) + nodes, path=step + path)


FuncRef = namedtuple('FuncRef', 'func count')


class TestTree(object):
    def __init__(self, funcitems):
        self._funcitems = funcitems
        # self._func2node = defaultdict(set())
        self._path2funcs = defaultdict([])
        self._node2children = defaultdict([])
        # self._mods = OrderedDict()

        # self._set((_root_id,), funcitems)
        self._root = Node(self, (_root_id,), funcitems)
        self._path2funcs[(_root_id,)].extend(items)
        for item in funcitems:
            nodes, path = get_modpath((item,))
            self._path2funcs[path].append(item)
            # self._set(path, (item,))
            # self._mods[path[0]] = Node(self, path, mod)
            loc = (_root_id,)
            for key, node in zip(path, nodes):
                self._node2children[loc].append(key)
                loc += key
                self._path2funcs[path].append(item)

    def _set(self, path, items):
        # fullpath = (_root_id,) + path
        # try:
        #     funcref = self._funcset[id(item)]
        #     funcref.count += 1
        # except KeyError:
        #     funcref = FuncRef(item, 0)  # use weakrefs here?
        #     self._funcset[id(item)] = funcref

    def _get_children(self, path):
        'return the children for a node'
        self._nodes[path]
        return

    def __getattr__(self, key):
        try:
            object.__getattribute__(self, key)
        except AttributeError as ae:
            try:
                return self._mods[key]
            except KeyError:
                raise ae

    def __dir__(self, key=None):
        return self._mods.keys()
        # if key:
        #     node = self._nodes[key]
        # else:
        #     node = self._nodes
        # return [path[0] for path in self._nodes.keys() if len(path) == 1 ]


class Node(object):
    def __init__(self, tree, path, funcref):
        self._tree = tree
        self._path = path
        self._fr = funcref

    # def __dir__(self):
        # return self._root.get_children

    def __getattr__(self, key):
        children = self._tree.get_children(self._path)
        return type(self)(self._tree, self._path, 

    def run(self):
        'run this test item'
        pass
