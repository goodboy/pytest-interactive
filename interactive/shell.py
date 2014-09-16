from IPython.terminal.embed import InteractiveShellEmbed
from IPython.core.magic import (Magics, magics_class, line_magic)
from IPython.core.history import HistoryManager


class PytestShellEmbed(InteractiveShellEmbed):

    def init_history(self):
        """Sets up the command history, and starts regular autosaves."""
        self.history_manager = HistoryManager(
            shell=self, parent=self, hist_file=self.pytest_hist_file)
        self.configurables.append(self.history_manager)

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


@magics_class
class SelectionMagics(Magics):

    def ns_eval(self, line):
        '''Evalutate line in the embedded ns and return result
        '''
        ns = self.shell.user_ns
        return eval(line, ns)

    @property
    def tt(self):
        return self.ns_eval('tt')

    @property
    def selection(self):
        return self.tt._selection

    @property
    def tr(self):
        return self.tt._tr

    @line_magic
    def add(self, line):
        '''add tests to the current selection
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
    def remove(self, line):
        '''remove tests from the current selection
        '''
        if self.selection:
            if ':' in line:
                return line
            else:
                    self.selection.clear()
        else:
            print("No tests currently selected?")

        # getter = operator.itemgetter(self.selection, line)
        # self.selection.remove(self.ns_eval(line))

    @line_magic
    def show(self, test_set):
        '''Show all currently selected test by pretty printing
        to the console.

        With no arguments this command is will display the currentlly selected
        set of tests. With a test set as an argument it will display all tests
        in the set.

        Usage:

            show:  print currently selected tests

            show <test_set>:  print all tests in test_set
        '''
        if test_set:
            ts = self.ns_eval(test_set)
            self.tt._tprint(ts._items)
        else:
            items = self.selection.values()
            if items:
                self.tt._tprint(items)
            else:
                self.tr.write("error: ", red=True)
                self.tr.write_line("No tests selected")
