"""
An extended shell for test selection
"""
import keyword 
import re
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.core.magic import (Magics, magics_class, line_magic)
from IPython.core.history import HistoryManager
from IPython.terminal.prompts import Prompts, Token


class TestCounterPrompt(Prompts):
    def in_prompt_tokens(self, cli=None):
        """Render a simple prompt which reports the number of currently
        selected tests.
        """
        return [
            (Token.PromptNum, '{}'.format(
                len(self.shell.user_ns['_selection']))),
            (Token.Prompt, ' selected >>> '),
        ]


class PytestShellEmbed(InteractiveShellEmbed):
    """Custom ip shell with a slightly altered exit message
    """
    prompts_class = TestCounterPrompt
    # cause if you don't use it shame on you
    editing_mode = 'vi'

    def init_history(self):
        """Sets up the command history, and starts regular autosaves.

        .. note::
            A separate history db is allocated for this plugin separate
            from regular shell sessions such that only relevant commands
            are retained.
        """
        self.history_manager = HistoryManager(
            shell=self, parent=self, hist_file=self.pytest_hist_file)
        self.configurables.append(self.history_manager)

    def exit(self):
        """Handle interactive exit.
        This method calls the ``ask_exit`` callback and if applicable prompts
        the user to verify the current test selection
        """
        if getattr(self, 'selection', None):
            print(" \n".join(self.selection.keys()))
            msg = "\nYou have selected the above {} test(s) to be run."\
                  "\nWould you like to run pytest now? ([y]/n)?"\
                  .format(len(self.selection))
        else:
            msg = 'Do you really want to exit ([y]/n)?'
        if self.ask_yes_no(msg, 'y'):
            # sets self.keep_running to False
            self.ask_exit()


@magics_class
class SelectionMagics(Magics):
    """Custom magics for performing multiple test selections
    within a single session
    """
    # XXX do we actually need this or can we do `user_ns` lookups?
    def ns_eval(self, line):
        '''Evalutate line in the embedded ns and return result
        '''
        ns = self.shell.user_ns
        return eval(line, ns)

    @property
    def tt(self):
        return self.ns_eval('_tree')

    @property
    def selection(self):
        return self.tt._selection

    @property
    def tr(self):
        return self.tt._tr

    def err(self, msg="No tests selected"):
        self.tt.err(msg)

    @line_magic
    def add(self, line):
        '''Add tests from a test set to the current selection.

        Usage:

        add tt : add all tests in the current tree
        add tt[4] : add 5th test in the current tree
        add tt.tests[1:10] : add tests 1-9 found under the 'tests' module
        '''
        if line:
            ts = self.ns_eval(line)
            if ts:
                self.selection.addtests(ts)
            else:
                raise TypeError("'{}' is not a test set".format(ts))
        else:
            print("No test set provided?")

    @line_magic
    def remove(self, line, delim=','):
        """Remove tests from the current selection using a slice syntax
        using a ',' delimiter instead of ':'.

        Usage:

        remove : remove all tests from the current selection
        remove -1 : remove the last item from the selection
        remove 1, : remove all but the first item (same as [1:])
        remove ,,-3 : remove every third item (same as [::-3])
        """
        selection = self.selection
        if not self.selection:
            self.err()
            return
        if not line:
            selection.clear()
            return
        # parse out slice
        if delim in line:
            slc = slice(*map(lambda x: int(x.strip()) if x.strip() else None,
                        line.split(delim)))
            for item in selection[slc]:
                selection.remove(item)
        else:  # just an index
            try:
                selection.remove(selection[int(line)])
            except ValueError:
                self.err("'{}' is not and index or slice?".format(line))

    @line_magic
    def show(self, test_set):
        '''Show all currently selected test by pretty printing
        to the console.

        Usage:

            show:  print currently selected tests
        '''
        items = self.selection.values()
        if items:
            self.tt._tprint(items)
        else:
            self.err()

    @line_magic
    def cache(self, line, ident='pytest/interactive'):
        """Store a set of tests in the pytest cache for retrieval in another
        session.

        Usage:

            cache: show a summary of names previously stored in the cache.

            cache del <name>: deletes the named entry from the cache.

            cache add <name> <target>: stores the named tests as target name.
        """
        cachedict = self.tt.get_cache_dict()
        if line:
            tokens = line.split()
            subcmd, name = tokens[0], tokens[1]

            if subcmd == 'del':  # delete an entry
                name = tokens[1]
                self.tt.set_cache_items(name, None)  # delete
                self.shell.user_ns.pop(name)
                self.tr.write(
                    "Deleted cache entry for '{}'\n".format(name))
                return

            elif subcmd == 'add':  # create a new entry
                target = tokens[2]
                if not re.match("[_A-Za-z][_a-zA-Z0-9]*$", target) \
                        and not keyword.iskeyword(name):
                    self.tt.err("'{}' is not a valid identifier"
                                .format(target))
                    return

                testset = self.ns_eval(name)
                self.tt.set_cache_items(target, testset)

                # update the local shell's ns
                if testset:
                    self.shell.user_ns[target] = testset
                self.tr.write(
                    "Created cache entry for '{}'\n".format(name))
                return

            self.tt.err("'{}' is invalid. See %cache? for usage.".format(line))
        else:
            tr = self.tr
            tr.write("\nSummary:\n", green=True)
            for name, testnames in cachedict.items():
                tr.write('{} -> {} items\n'.format(name, len(testnames)))
