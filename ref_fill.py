import sublime
import sublime_plugin
import os
from . import ref_finder

reference_server = ref_finder.ReferenceFinder()

class RefFiller(sublime_plugin.ViewEventListener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.region = None

    def on_query_context(self, key, operator, operand, match_all):
        if self.view.score_selector(self.view.sel()[0].b, "text.tex.latex"):
            prefix = self.view.substr(self.view.word(self.view.sel()[0].b))
            if prefix == "ref":
                print(prefix)
                self.view.window().show_quick_panel(reference_server.deliver_entries(), self.on_apply_selection, sublime.MONOSPACE_FONT)

                # region = view.word(view.sel()[0])
                # self.view.run_command("texcuite_apply_ref", {"entry": "blafoo "})
                return False

            return False

        return None

    def on_apply_selection(self, number):
        self.view.run_command("texcuite_apply_ref", {"number": number})
        print(number)
                



class TexcuiteApplyRefCommand(sublime_plugin.TextCommand):
    def run(self, edit, number):
        if number != -1:
            exp = self.view.word(self.view.sel()[0])
            self.view.replace(edit, exp, reference_server.query_entry(number))


class ReferenceWatchdog(sublime_plugin.ViewEventListener):
    def on_activated(self):
        if self.view.score_selector(self.view.sel()[0].b, "text.tex.latex"):
            current_dir = os.path.dirname(self.view.file_name())
            if reference_server.rootdir != current_dir:
                reference_server.update_references(current_dir)
