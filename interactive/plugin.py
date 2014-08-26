import _pytest
import pytest
import pprint
from collections import OrderedDict, namedtuple
from IPython.terminal.embed import InteractiveShellEmbed


class PytestShellEmbed(InteractiveShellEmbed):

    def exit(self):
        """Handle interactive exit.
        This method calls the ask_exit callback.
        """
        if getattr(self, 'test_items', None):
            print(" \n".join(self.test_items.keys()))
            msg = "You have selected the above {} test(s) to be run."\
                  "\nWould you like to run pytest now? ([y]/n)?"\
                  .format(len(self.test_items))
        else:
            msg = 'Do you really want to exit ([y]/n)?'
        if self.ask_yes_no(msg, 'y'):
            self.ask_exit()


def pytest_addoption(parser):
    parser.addoption("--interactive", "--ia", action="store_true",
                     dest='interactive',
                     help="enable iteractive selection of tests after"
                     " collection")


def pytest_keyboard_interrupt(excinfo):
    'enter the debugger on keyboard interrupt'
    pytest.set_trace()


def pytest_collection_modifyitems(session, config, items):
    """
    called after collection has been performed, may filter or re-order
    the items in-place.
    """
    if not (config.option.interactive and items):
        return

    # prep and embed ipython
    ipshell = PytestShellEmbed(banner1='Entering IPython workspace...',
                               exit_msg='Exiting IPython...Running pytest')
    # build a tree of test items
    tt = TestTree(items, ipshell)

    # FIXME: can we operate on the cls directly and avoid
    # poluting our namespace with items?
    # set the prompt to track number of selected test items
    pm = ipshell.prompt_manager
    bold_prmpt = '{color.number}' '{tt}' '{color.prompt}'
    pm.in_template = "'{}' selected >>> ".format(bold_prmpt)
    # don't rjustify with preceding 'in' prompt
    pm.justify = False

    msg = """Welcome to pytest-interactive, the pytest + ipython sensation.\n
Please explore the test (collection) tree using tt.<TAB>\n
When finshed tabbing to a test node, simply call it to have
pytest invoke all tests selected under that node."""

    def embed(tt, items):
        # FIXME: can we add the startup banner before the call?
        ipshell(msg)

    # embed
    embed(tt, items)

    # make selection
    items[:] = tt.selection.values()[:]


_root_id = '.'
Package = namedtuple('Package', 'name path node parent')


class ParametrizedFunc(object):
    def __init__(self, name, funcitems, parent):
        self.funcitems = OrderedDict()
        self.parent = parent
        if not isinstance(funcitems, list):
            instances = [funcitems]
        for item in instances:
            self.append(item)

    def append(self, item):
        self.funcitems[item.callspec.id] = item

    def __getitem__(self, key):
        return self.funcitems[key]

    def __dir__(self):
        attrs = sorted(set(dir(type(self)) +
                       list(self.__dict__.keys())))
        return self.funcitems.keys() + attrs


def gen_nodes(item, cache):
    '''generate all parent objs of this node up to the root/session'''
    path = ()
    # pytest call which lists branch items in order
    chain = item.listchain()
    for node in chain:
        try:
            name = node._obj.__name__
        except AttributeError as ae:
            # when either Instance or non-packaged module
            if isinstance(node, _pytest.python.Instance):
            # leave out Instances, later versions are going to drop them anyway
                continue
            elif node.nodeid is _root_id:
                name = _root_id
            else:  # should never get here
                raise ae
        # packaged module
        if '.' in name and isinstance(node, _pytest.python.Module):
            # import ipdb
            # ipdb.set_trace()
            # FIXME: this should be cwd dependent!!!
            # (i.e. don't add package objects we're below in the fs)
            prefix = tuple(name.split('.'))
            lpath = node.fspath
            fspath = str(lpath)
            # don't include the mod name in path
            for level in prefix[:-1]:
                name = '{}{}'.format(fspath[:fspath.index(level)], level)
                path += (level,)
                yield path, Package(name, lpath, node, node.parent)
            name = prefix[-1]  # this mod's name
        # func item
        elif isinstance(node, _pytest.python.Function):
            name = node.name
            if '[' in name:
                funcname = name.split('[')[0]
                try:
                    # TODO: look up the pf based on the vanilla func obj
                    # (should be an attr on the _pyfuncitem...)
                    pf = cache[path + (funcname,)]
                    pf.append(node)
                except KeyError:
                    pf = ParametrizedFunc(name, node, node.parent)
                path += (funcname,)
                yield path, pf
        path += (name,)
        yield path, node


class TestTree(object):
    def __init__(self, funcitems, ipshell):
        self._funcitems = funcitems  # never modify this
        self.selection = OrderedDict()  # items must be unique
        self._path2items = OrderedDict()
        self._path2children = {}  # defaultdict(set)
        self._sp2items = {}  # selection property to items
        self._selected = False
        self._nodes = {}
        self._cache = {}
        for item in funcitems:
            for path, node in gen_nodes(item, self._nodes):
                self._path2items.setdefault(path, list()).append(item)
                # self._sp2items
                if path not in self._nodes:
                    self._nodes[path] = node
                    self._path2children.setdefault(path[:-1], set()).add(path)
        self._root = Node(self, (_root_id,))

        # ipython shell
        self._shell = ipshell
        self._shell.test_items = self.selection

    def __str__(self):
        '''stringify current selection length'''
        return str(len(self.selection))

    # def _get_children(self, path):
    #     'return all children for the node given by path'
    #     return self._path2children[path]

    def __getattr__(self, key):
        try:
            object.__getattribute__(self, key)
        except AttributeError as ae:
            try:
                return getattr(self._root, key)
            except AttributeError:
                raise ae

    def __dir__(self, key=None):
        attrs = sorted(set(dir(type(self)) + list(self.__dict__.keys())))
        return dir(self._root) + attrs

    def _runall(self, path=None):
        # XXX can this selection remain ordered to avoid
        # traversing the list again?...imagined speed gain in my head?
        if path:
            # items = self._path2items[path]
            for item in self._path2items[path]:
                self.selection[item.nodeid] = item
            # self.selection.extend([f for f in self._funcitems if f in items])

        if not self._selected:
            self._selected = True
        self._shell.exit()


class Node(object):
    '''Represent a pytest node/item for use as a tab complete-able object
    for use with ipython. An internal reference is kept to the real Node.
    Most operations are delegated to the containing TestTree.
    '''
    def __init__(self, tree, path):
        self._tree = tree
        self._path = path
        self._len = len(path)

    def __dir__(self):
        if isinstance(self._node, ParametrizedFunc):
            return self._node._instances.keys()
        else:
            return sorted([key[self._len] for key in self._children])

    def __repr__(self):
        clsname = self._node.__class__.__name__
        nodename = getattr(self._node, 'name', None)
        return "<{} '{}' -> {} tests>".format(str(clsname), nodename,
                                              len(self._items))

    @property
    def _children(self):
        return self._tree._path2children[self._path]

    def _get_items(self):
        return self._tree._path2items[self._path]

    _items = property(_get_items)

    def __getitem__(self, key):
        if isinstance(key, int):
            item = self._items[key]
            # self._tree.selection.append(self._items[key])
            self._tree.selection[item.nodeid] = item
        if isinstance(key, slice):
            # self._tree.selection.extend(self._items[key])
            items = self._items[key]
            for item in items:
                self._tree.selection[item.nodeid] = item

    def __call__(self, key=None):
        """Run all tests under this node"""
        if key is None:
            path = self._path
        else:
            path = None
            self[key]  # select tests specified by key
        return self._tree._runall(path)

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
                raise AttributeError("sub-node '{}' can not be found"
                                     .format(attr))

    def show(self):
        """Show all test items under this node on the console
        """
        # pprint.pprint(
        # for child in self._childen
        pprint.pprint([node.nodeid for node in self._items])

    def _get_node(self, path=None):
        if not path:
            path = self._path
        return self._tree._nodes[path]

    _node = property(_get_node)

    def _sub(self, key):
        'return a (new/cached) sub node'
        if key is 'parent':
            path = self._path[:-1]
        else:
            path = self._path + (key,)
        return self._tree._cache.setdefault(path, type(self)(self._tree, path))
