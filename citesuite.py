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
        self.bibphantoms = bibphantoms.BibPhantomManager()
        self.errors = {}
        self.properties = dict()
        self._bib_focus = False # used for "goto BibTex entry", wait until bib file is parsed, then scroll to symbol

    def on_hover(self, point, hover_zone):
        # scopes = self.view.scope_name(self.view.sel()[0].begin()).split()
        scopes = self.view.scope_name(point).split()
        if 'text.tex.latex' in scopes and 'constant.other.citation.latex' in scopes:
            
            # print(self.view.substr(self.view.expand_by_class(point, sublime.CLASS_WORD_END | sublime.CLASS_WORD_START, '\{\},')))
            cite_key = self.view.substr(self.view.expand_by_class(point, sublime.CLASS_WORD_END | sublime.CLASS_WORD_START, '\{\},'))
            image_path, self.properties = self.bibmanager.serve_entry(cite_key)
            print(self.properties)
            info_content = ""
            if image_path:
                if "ref" in self.properties:
                    info_content += "<h3>[{}]</h3>\n".format(self.properties["ref"])
                info_content += """<p><img src="file://{}"></p>\n""".format(image_path)
                info_content += """<a href="gotobib">BibTeX entry</a>"""
                self.view.show_popup(info_content, sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, max_width=800, on_navigate=self.handle_popup)

    def handle_popup(self, command):
        print(command)
        if command == "gotobib":
            bib_view = self.view.window().open_file(self.properties["bibfile"])
            bib_view.show(next(filter(lambda x: x[1] == self.properties['key'], bib_view.symbols()), None)[0])

            

    def on_activated_async(self):
        scope = self.view.scope_name(0)
        self.logger.debug("Scope of view is {}".format(scope))
        if self.view.file_name() is not None and ("text.tex.latex" in scope.split() or self.view.file_name().endswith('.bib')):
            self.logger.debug("Changed views to {}".format(self.view.file_name()))

            # adjust rendering style to project
            project_data = self.view.window().project_data()
            project_settings = project_data['settings'] if(project_data is not None and "settings" in project_data) else {}
            if "bibstyle" in project_settings:
                self.bibmanager.set_style(project_settings['bibstyle'])

            self.errors = self.bibmanager.refresh_all_entries(self.view.window().project_data(), self.view.file_name())
            if self.view.file_name().endswith('.bib'):
                self.bibphantoms.update_phantoms(self.view, self.errors[self.view.file_name()], self.view.symbols())
                self.logger.debug(self.view.file_name())
                self.logger.debug(self.errors)


    def on_post_save_async(self):
        if self.view.file_name().endswith('.bib'):
            self.errors = self.bibmanager.refresh_all_entries(self.view.window().project_data(), self.view.file_name())
            self.bibphantoms.update_phantoms(self.view, self.errors[self.view.file_name()], self.view.symbols())


