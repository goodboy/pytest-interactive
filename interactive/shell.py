from IPython.terminal.embed import InteractiveShellEmbed
from IPython.core.magic import (Magics, magics_class, line_magic)


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


@magics_class
class SelectionMagics(Magics):

    def _ns_lookup(self, line):
        '''Look up an object in the embedded ns
        and return it
        '''
        ns = self.shell.user_ns
        try:
            return eval(line, ns)
        except NameError:
            # FIXME: do we even need this?
            root, sep, tail = line.partition('.')
            obj = ns[root]
            if tail:
                obj = operator.attrgetter(tail)(obj)
            return obj

    @property
    def selection(self):
        return self._ns_lookup('tt._selection')

    @line_magic
    def add(self, line):
        'add tests to the current selection'
        ts = self._ns_lookup(line)
        self.selection.addtests(ts)

    @line_magic
    def remove(self, line):
        'remove tests from the current selection'
        if ':' in line:
            return line
        else:
            self.selection.clear()
        # getter = operator.itemgetter(self.selection, line)
        # self.selection.remove(self._ns_lookup(line))

    @line_magic
    def show(self, line):
        '''show all currently selected test'''
        return self.selection.items()
