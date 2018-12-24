import sublime
import sublime_plugin
import json
from os.path import join as path_join
from os.path import basename as basename
import re
import logging
from . import bibmanager
from . import bibphantoms


class HoverCite(sublime_plugin.ViewEventListener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger()
        # self.logger.setLevel(logging.DEBUG)
        self.stream = logging.StreamHandler()
        self.stream.setLevel(logging.INFO)
        self.logger.addHandler(self.stream)
        self.bibmanager = bibmanager.BibManager(self.logger)
        self.bibmanager.set_style('alpha')
        self.bibphantoms = bibphantoms.BibPhantomManager()
        self.errors = {}

    def on_hover(self, point, hover_zone):
        # scopes = self.view.scope_name(self.view.sel()[0].begin()).split()
        scopes = self.view.scope_name(point).split()
        if 'text.tex.latex' in scopes and 'constant.other.citation.latex' in scopes:
            # print("Hovered over cite")
            # print(self.view.substr(self.view.expand_by_class(point, sublime.CLASS_WORD_END | sublime.CLASS_WORD_START, '\{\},')))
            cite_key = self.view.substr(self.view.expand_by_class(point, sublime.CLASS_WORD_END | sublime.CLASS_WORD_START, '\{\},'))
            image_path, properties = self.bibmanager.serve_entry(cite_key)
            info_content = ""
            if image_path:
                if "ref" in properties:
                    info_content += "<h3>[{}]</h3>\n".format(properties["ref"])
                info_content += """<p><img src="file://{}"></p>\n""".format(image_path)
                info_content += """<p><a href="gotobib">BibTeX entry</a><p>"""
                self.view.show_popup(info_content, sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, max_width=800, on_navigate=self.handle_popup)

    def handle_popup(self, command):
        print(command)

    def on_activated_async(self):
        scope = self.view.scope_name(0)
        self.logger.debug("Scope of view is {}".format(scope))
        if self.view.file_name() is not None and ("text.tex.latex" in scope.split() or self.view.file_name().endswith('.bib')):
            self.logger.debug("Changed views to {}".format(self.view.file_name()))
            self.errors = self.bibmanager.refresh_all_entries(self.view.window().project_data(), self.view.file_name())
            if self.view.file_name().endswith('.bib'):
                self.bibphantoms.update_phantoms(self.view, self.errors[self.view.file_name()], self.view.symbols())
                self.logger.debug(self.view.file_name())
                self.logger.debug(self.errors)
                # print(self.view.symbols())
    def on_post_save_async(self):
        if self.view.file_name().endswith('.bib'):
            self.errors = self.bibmanager.refresh_all_entries(self.view.window().project_data(), self.view.file_name())
            self.bibphantoms.update_phantoms(self.view, self.errors[self.view.file_name()], self.view.symbols())
