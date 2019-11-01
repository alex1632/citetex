# Menu-based reference completion

import sublime
import sublime_plugin
import html
import os
from threading import Lock
from . import ref_handler

reference_server = ref_handler.ReferenceHandler()

class RefFiller(sublime_plugin.ViewEventListener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.region = None
        self.entry = None


    def on_query_context(self, key, operator, operand, match_all):
        '''
        Reference autocompletion trigger (ref)
        If no references are declared, ordinary word completion is performed
        '''
        if self.view.score_selector(self.view.sel()[0].b, "text.tex.latex") \
            and operand == True and key == "bh_wrapping":
            prefix = self.view.substr(self.view.word(self.view.sel()[0].b))
            if prefix == "ref":
                self.view.window().show_quick_panel(reference_server.deliver_entries(), self.on_apply_selection)
                return False

            return None
        return None

    def on_hover(self, point, hover_zone):
        scopes = self.view.scope_name(point).split()
        if 'text.tex.latex' in scopes and 'constant.other.reference.latex' in scopes:
            ref_key = self.view.substr(self.view.expand_by_class(point, sublime.CLASS_WORD_END | sublime.CLASS_WORD_START, '\{\},'))

            self.entry = reference_server.query_popup(ref_key)
            if self.entry:
                info_content = ""
                info_content += "<h3>{}</h3>\n".format(html.escape(self.entry["text"]))
                info_content += '<p>[{}] in {} - <a href="definition">Go to Definition</a></p>\n'.format(self.entry["type"].title(), os.path.basename(self.entry["filename"]))
                
                self.view.show_popup(info_content, sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, max_width=800, on_navigate=self._handle_popup)
    
    def _handle_popup(self, command):
        if command == "definition":
            tex_view = self.view.window().open_file(self.entry["filename"])
            tex_view.show(next(filter(lambda x: x[1] == self.entry['label'], tex_view.symbols()), (None, ))[0])


    def on_apply_selection(self, number):
        if number != -1: # if selection is not aborted
            self.view.run_command("citetex_apply_ref", {"number": number})              

    def on_activated(self):
        if self.view.score_selector(self.view.sel()[0].b, "text.tex.latex"):
            current_dir = os.path.dirname(self.view.file_name())
            if reference_server.rootdir != current_dir:
                reference_server.update_references(current_dir)

    def on_post_save(self):
        if self.view.file_name().endswith('.tex'):
            print("Updating {}".format(self.view.file_name()))
            reference_server.update_file(self.view.file_name())



class CitetexApplyRefCommand(sublime_plugin.TextCommand):
    def run(self, edit, number):
        default_settings = sublime.load_settings("CiteTeX-default.sublime-settings")
        user_settings = sublime.load_settings("CiteTeX-user.sublime-settings")
        exp = self.view.word(self.view.sel()[0])
        self.view.replace(edit, exp, reference_server.query_entry(number,
                                                                  user_settings,
                                                                  default_settings,
                                                                  self.view.window().project_data()))

class CitetexGotoLabelCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_quick_panel(reference_server.deliver_entries(), self.on_apply_selection)

    def on_apply_selection(self, sel):
        entry = reference_server.entries[sel]
        tex_view = self.window.open_file(entry["filename"])
        tex_view.show_at_center(next(filter(lambda x: x[1] == entry['label'], tex_view.symbols()), None)[0].a)
        