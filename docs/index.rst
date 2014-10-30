pytest-interactive: select tests to run using IPython
===========================================================
This handy plugin allows for the selection and run of pytest tests
using the command line facilities available in `IPython <http://ipython.org/>`_.
This includes tab completion along the pytest node hierarchy and test callspec
ids as well as the use of standard python subscript and slice syntax for selection.

Upon invocation with either the ``--interactive`` or shorthand ``--ia`` arguments,
you will enter an interactive python shell which allows for navigation of the test
tree built during pytest's collection phase.

Enjoy and feel free to submit a pull request or any bugs on my
`github page`_

.. _github page: https://github.com/tgoodlet/pytest-interactive

.. contents::
    :local:
    :backlinks: entry


Quickstart
----------
To invoke the interactive plugin simply run pytest as normal from the top of
your test tree like so

.. code-block:: console

    $ py.test -vvvs --interactive example_test_set/

or more compactly

.. code-block:: console

    $ py.test -vvvs --ia example_test_set/


Pytest will execute normally up until the end of the collection phase at
which point it will enter a slightly customized ipython shell

.. code-block:: python

    ============================ test session starts ============================
    platform linux -- Python 3.4.1 -- py-1.4.20 -- pytest-2.5.2 -- /usr/bin/python
    plugins: interactive
    collected 63 items
    building test tree...
    entering ipython workspace...

    Welcome to pytest-interactive, the pytest + ipython sensation.
    Please explore the test (collection) tree using tt.<TAB>
    When finished tabbing to a test node, simply call it to have
    pytest invoke all tests collected under that node.

Look, a nice set of instructions to follow

.. code-block:: python

    '0' selected >>>

    '0' selected >>> tt.<TAB>
    tt.test_pinky_strength  tt.test_dogs_breath
    tt.test_manliness       tt.test_cats_meow

    '0' selected >>> tt.testsdir.test_pinky_strength.<TAB>
    tt.test_pinky_strength.test_contrived_name_0
    tt.test_pinky_strength.test_the_readers_patience

That's right, jacked pinky here you come...


Select tests via tab-completion
-----------------------------------
Basic tab completion should allow you to navigate to the test(s) of interest
as well as aid in exploring the overall pytest collection tree.

Tab completion works along python packages, modules, classes and test
functions
The latter three types are collected as nodes by pytest out of the box
but as an extra aid, intermediary nodes are created for packages containing
tests as well.
This is helpful to distinguish between different groups of tests in the file
system.

.. note::
    The binding ``tt`` (abbreviation for *test tree*) is a reference to the
    root of a tree of nodes which roughly corresponds to the collection tree
    gathered by pytest.

If you'd like to see all tests included by a particular node simply
evaluate it on the shell to trigger a pretty print ``repr`` method:

.. code-block:: python

    '0' selected >>> tt.tests.subsets.test_setA
    Out [0]:
       <Module 'example_test_set/tests/subsets/test_setA.py'>
    0    <Function 'test_modes[a]'>
    1    <Function 'test_modes[b]'>
    2    <Function 'test_modes[c]'>
    3    <Function 'test_inputs[1]'>
    4    <Function 'test_inputs[2]'>
    5    <Function 'test_inputs[3]'>
         <Class 'TestBoth'>
    6      <Function 'test_m[a-1]'>
    7      <Function 'test_m[a-2]'>
    8      <Function 'test_m[a-3]'>
    9      <Function 'test_m[b-1]'>
    10     <Function 'test_m[b-2]'>
    11     <Function 'test_m[b-3]'>
    12     <Function 'test_m[c-1]'>
    13     <Function 'test_m[c-2]'>
    14     <Function 'test_m[c-3]'>
    <TestSet for 'example_test_set/tests/subsets/test_setA.py' -> 15 tests>

When ready to run pytest, simply ``__call__`` the current node to exit the shell
and invoke all tests below it in the tree:

.. code-block:: python

    '0' selected >>> tt.test_setB.test_modes()

.. code-block:: python

    example_test_set/tests/subsets/subsubset/test_setB.py::test_modes[a]
    example_test_set/tests/subsets/subsubset/test_setB.py::test_modes[b]
    example_test_set/tests/subsets/subsubset/test_setB.py::test_modes[c]

    You have selected the above 3 test(s) to be run.
    Would you like to run pytest now? ([y]/n)?
    <ENTER>

    exiting shell...

    example_test_set/tests/subsets/subsubset/test_setB.py:41: test_modes[a] PASSED
    example_test_set/tests/subsets/subsubset/test_setB.py:41: test_modes[b] PASSED
    example_test_set/tests/subsets/subsubset/test_setB.py:41: test_modes[c] FAILED


Selection by index or slice
---------------------------
Tests can also be selected by slice or subscript notation. This is handy
if you see the test(s) you'd like to run in the pretty print output but
don't feel like tab-completing all the way down the tree to the
necessary leaf node.

Take the following subtree of tests for example:

.. code-block:: python

    '0' selected >>> tt.test_setB.test_modes
    Out[1]:
      <Module 'example_test_set/tests/subsets/subsubset/test_setB.py'>
    0   <Function 'test_modes[a]'>
    1   <Function 'test_modes[b]'>
    2   <Function 'test_modes[c]'>
    <TestSet for 'None' -> 3 tests>

Now let's select the last test

.. code-block:: python

    '0' selected >>> tt.test_setB.test_modes[-1]
    Out[2]:
      <Module 'example_test_set/tests/subsets/subsubset/test_setB.py'>
    0   <Function 'test_modes[c]'>
    <TestSet for 'None' -> 1 tests>


Or how about the first two

.. code-block:: python

    '0' selected >>> tt.test_setB.test_modes[:2]
    Out[52]:
      <Module 'example_test_set/tests/subsets/subsubset/test_setB.py'>
    0   <Function 'test_modes[a]'>
    1   <Function 'test_modes[b]'>
    <TestSet for 'None' -> 2 tests>

You can of course ``__call__`` the indexed node as well to immediately run
all tests in the selection.


Filtering by parameterized test callspec ids
--------------------------------------------
Tests which are generated at runtime (aka parametrized) can be filtered
by their callspec ids. Normally the ids are shown inside the
braces ``[...]`` of the test *nodeid* which often looks someting like:

``<Function 'test_some_feature[blah-mode5-ipv6]'>``

(i.e. what you get for output when using the ``--collectonly``  arg)

.. not sure why the params ref below doesn't link internally ...

To access the available ids use the node's
:py:attr:`~interactive.plugin.TestSet.params` attribute.

.. code-block:: python

    '0' selected >>> tt.params.<TAB>
    tt.params.a      tt.params.b      tt.params.c      tt.params.cat
    tt.params.dog    tt.params.mouse

    '0' selected >>> tt.params.a
    Out[2]:
       <Module 'example_test_set/tests/test_set_root.py'>
    0    <Function 'test_modes[a]'>
         <Class 'TestBoth'>
    1      <Function 'test_m[a-dog]'>
    2      <Function 'test_m[a-cat]'>
    3      <Function 'test_m[a-mouse]'>
       <Module 'example_test_set/tests/subsets/test_setA.py'>
    4    <Function 'test_modes[a]'>
         <Class 'TestBoth'>
    5      <Function 'test_m[a-1]'>
    6      <Function 'test_m[a-2]'>
    7      <Function 'test_m[a-3]'>
       <Module 'example_test_set/tests/subsets/subsubset/test_setB.py'>
    8    <Function 'test_modes[a]'>
         <Class 'TestBoth'>
    9      <Function 'test_m[a-1]'>
    10     <Function 'test_m[a-2]'>
    11     <Function 'test_m[a-3]'>
       <Module 'example_test_set/tests2/test_set_root2.py'>
    12   <Function 'test_modes[a]'>
         <Class 'TestBoth'>
    13     <Function 'test_m[a-1]'>
    14     <Function 'test_m[a-2]'>
    15     <Function 'test_m[a-3]'>
    <TestSet for 'pytest-interactive' -> 16 tests>

You can continue to filter this way as much as you'd like

.. code-block:: python

    '0' selected >>> tt.params.a.params.<TAB>
    tt.params.a.params.cat    tt.params.a.params.dog
    tt.params.a.params.mouse

    '0' selected >>> tt.params.a.params.mouse
    Out[3]:
      <Module 'example_test_set/tests/test_set_root.py'>
        <Class 'TestBoth'>
    0     <Function 'test_m[a-mouse]'>
    <TestSet for 'pytest-interactive' -> 1 tests>

.. warning::
    There is one stipulation with using id filtering which is that
    the id tokens must be valid python literals. Otherwise the
    :py:meth:`__getattr__` overloading of the node will not work.
    It is recomended that you give your parameterized tests tab
    completion friendly ids using the `ids kwarg`_ as documented on the
    pytest site.

.. _ids kwarg: http://pytest.org/latest/parametrize.html
    #_pytest.python.Metafunc.parametrize


Multiple selections and magics
------------------------------
So by now I'm sure you've thought *oh hey this is damn neat, but what if
I want to select tests from totally different parts of the tree??*

Well lucky for you some %magics have been added to the shell to help with just
that problem:

.. code-block:: python

    '0' selected >>> tt.test_setB.test_modes
    Out[1]:
      <Module 'example_test_set/tests/subsets/subsubset/test_setB.py'>
    0   <Function 'test_modes[a]'>
    1   <Function 'test_modes[b]'>
    2   <Function 'test_modes[c]'>
    <TestSet for 'None' -> 3 tests>

    '0' selected >>> add tt.test_setB.test_modes[-2:]

    '2' selected >>>

You can easily show the contents of your selection

.. code-block:: python

    '2' selected >>> show
      <Module 'example_test_set/tests/subsets/subsubset/test_setB.py'>
    0   <Function 'test_modes[b]'>
    1   <Function 'test_modes[c]'>

    '2' selected >>>

You can also remove tests from the current selection by index

.. code-block:: python

    '2' selected >>> remove 1

    '1' selected >>> show
     <Module 'example_test_set/tests/subsets/subsubset/test_setB.py'>
    0  <Function 'test_modes[b]'>

    '1' selected >>>

When ready to run your tests simply exit the shell

.. code-block:: python

    '1' selected >>> <CTRL-D>
    example_test_set/tests/subsets/subsubset/test_setB.py::test_modes[b]

    You have selected the above 1 test(s) to be run.
    Would you like to run pytest now? ([y]/n)?

For additional docs on the above shell %magics simply use the ``%?`` magic
syntax available in the IPython shell (i.e. ``add?`` or ``remove?`` or
``show?``).


Internal reference
------------------
.. toctree::
    :maxdepth: 3

    plugin
    shell


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
