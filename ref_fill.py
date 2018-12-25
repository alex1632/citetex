import sublime
import sublime_plugin
import os
from . import ref_finder

reference_server = ref_finder.ReferenceFinder()

class RefFiller(sublime_plugin.EventListener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.region = None

    def on_query_context(self, view, key, operator, operand, match_all):
        if view.score_selector(view.sel()[0].b, "text.tex.latex"):
            prefix = view.substr(view.word(view.sel()[0].b))
            if prefix == "ref":
                print(prefix)
                # region = view.word(view.sel()[0])
                self.view = view
                # view.run_command("texcuite_apply_ref", {"entry": "blafoo "})
                return True

            return False

        return None
                


    def on_apply_selection(self, number):
        self.view.run_command("texcuite_apply_ref", {"entry": "blafoo "})


class TexcuiteApplyRefCommand(sublime_plugin.TextCommand):
    def run(self, edit, entry):
        exp = self.view.word(self.view.sel()[0])
        print(exp)
        print(self.view.substr(exp))
        self.view.replace(edit, exp, entry)


class ReferenceWatchdog(sublime_plugin.ViewEventListener):
    def on_activated(self):
        if self.view.score_selector(self.view.sel()[0].b, "text.tex.latex"):
            current_dir = os.path.dirname(self.view.file_name())
            if reference_server.rootdir != current_dir:
                reference_server.update_references(current_dir)
