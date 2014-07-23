import _pytest
from collections import OrderedDict, namedtuple
import IPython

def pytest_addoption(parser):
    parser.addoption("--i", "--interactive", action="store_true",
            dest='interactive',
            help="enable iteractive selection of tests after collection")


def pytest_collection_modifyitems(session, config, items):
    """called after collection has been performed, may filter or re-order
    the items in-place."""
    if not config.option.interactive:
        return

    root = ItemTree(items)
    # build a tree of test items
    IPython.embed()


def get_modpath(node, path=()):
    '''return the eldest parent of this node
    a child of the root/session'''
    try:
        step = (node._obj.__name__,)
    except AttributeError:
        step = ()  # don't bother with the instance node/step
    if node.parent.nodeid == '.':  # the root/session
        return node, step + path
    if node.parent:
        return get_modpath(node.parent, path=step + path)


FuncRef = namedtuple('FuncRef', 'func count')


class ItemTree(object):
    def __init__(self, funcitems):
        self._funcset = funcitems
        self._nodes = {} #OrderedDict({})
        self._mods = {}
        for item in funcitems:
            mod, path = get_modpath(item)
            self._mods[path[0]] = mod
            self._set(path, item)
            for i, key in enumerate(path):
                self._set((path[i],), item)

    def _set(self, path, item):
        # try:
        #     funcref = self._funcset[id(item)]
        #     funcref.count += 1
        # except KeyError:
        #     funcref = FuncRef(item, 0)  # use weakrefs here?
        #     self._funcset[id(item)] = funcref
        self._nodes[path] = Node(self, path, item)

    def _get_children(self, path):
        'return the children for a node'
        self._nodes[path]
        return

    def __getattr__(self, key):
        try:
            object.__getattribute__(self, key)
        except AttributeError as ae:
            try:
                return self._nodes[(key,)]
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
    def __init__(self, root, path, funcref):
        self._root = root
        self._path = path
        self._fr = funcref

    # def __dir__(self):
        # return self._root.get_children

    def __setattr__(self, key, value):
        pass

    def __getattr__(self, key):
        return self.root.key

    # def __repr__(self):
    #     pass

    def run(self):
        'run this test item'
        pass
