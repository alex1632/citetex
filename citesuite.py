from threading import Lock
import sublime
import sublime_plugin
import os
from . import bibmanager
from . import bibphantoms

def plugin_loaded():
    try:
        os.makedirs(os.path.join(sublime.cache_path(), "texcuite"))
    except OSError:
        pass

    HoverCite.bibman.set_cache_path(sublime.cache_path())

    print("citesuite loaded")


class HoverCite(sublime_plugin.ViewEventListener):
    # these cannot be per-instance since focusing on file load would not work.
    bibman = bibmanager.BibManager()
    bibphan = bibphantoms.BibPhantomManager()
    LOAD_PENDING = None
    mutex = Lock()
    current_properties = dict()
    current_path = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = dict()

        self._user_settings = None
        self._default_settings = None
        HoverCite.bibman.set_style("alpha")

    def use_settings(self):
        self._user_settings = sublime.load_settings("TeXCuite-user.sublime-settings")
        self._default_settings = sublime.load_settings("TeXCuite-default.sublime-settings")


    def on_hover(self, point, hover_zone):
        scopes = self.view.scope_name(point).split()
        if 'text.tex.latex' in scopes and 'constant.other.citation.latex' in scopes:
            # print(self.view.substr(self.view.expand_by_class(point, sublime.CLASS_WORD_END | sublime.CLASS_WORD_START, '\{\},')))
            cite_key = self.view.substr(self.view.expand_by_class(point, sublime.CLASS_WORD_END | sublime.CLASS_WORD_START, '\{\},'))
            image_path, HoverCite.current_properties = HoverCite.bibman.serve_entry(cite_key)
            print(image_path)
            info_content = ""
            if image_path:
                if "ref" in HoverCite.current_properties:
                    info_content += "<h3>[{}]</h3>\n".format(HoverCite.current_properties["ref"])
                info_content += """<p><img src="file://{}"></p>\n""".format(image_path)
                info_content += """<a href="gotobib">BibTeX entry</a>"""
                self.view.show_popup(info_content, sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, max_width=800, on_navigate=self.handle_popup)

    def handle_popup(self, command):
        if command == "gotobib":
            bib_view = self.view.window().open_file(HoverCite.current_properties["bibfile"])
            if bib_view.is_loading():
                with HoverCite.mutex:
                    HoverCite.LOAD_PENDING = True
            else:
                marker = next(filter(lambda x: x[1] == HoverCite.current_properties['key'], bib_view.symbols()), None)[0]
                bib_view.show_at_center(marker)

    def on_load_async(self):
        with HoverCite.mutex:
            if HoverCite.LOAD_PENDING and "text.biblatex" in self.view.scope_name(self.view.sel()[0].a).split():
                self.view.show_at_center(next(filter(lambda x: x[1] == HoverCite.current_properties['key'], self.view.symbols()), None)[0])
                HoverCite.LOAD_PENDING = None
            

    def on_activated_async(self):
        file_name = self.view.file_name()
        path_of_file = os.path.dirname(file_name) if file_name else None
        scope = self.view.scope_name(0)
        if self.view.file_name() is not None and ("text.tex.latex" in scope.split() or self.view.file_name().endswith('.bib')):
            if path_of_file != HoverCite.current_path:
                HoverCite.current_path = path_of_file
                self.use_settings() # since we use settings, reload them
                # adjust rendering style to project
                project_data = self.view.window().project_data()
                project_settings = project_data['settings'] if(project_data is not None and "settings" in project_data) else {}
                
                if "bibstyle" in project_settings:
                    HoverCite.bibman.set_style(project_settings['bibstyle'])
                
                self.errors = HoverCite.bibman.refresh_all_entries(self.view.window().project_data(), self.view.file_name())

                if self.view.file_name().endswith('.bib'):
                    if self._user_settings.get("bib_errors", self._default_settings.get("bib_errors")):
                        HoverCite.bibphan.update_phantoms(self.view, self.errors[self.view.file_name()], self.view.symbols())
                    else:
                        HoverCite.bibphan.clear_phantoms()

    def on_post_save_async(self):
        if self.view.file_name().endswith('.bib'):
            self.use_settings()
            if self._user_settings.get("bib_errors", self._default_settings.get("bib_errors")):
                self.errors = HoverCite.bibman.refresh_all_entries(self.view.window().project_data(), self.view.file_name())
                HoverCite.bibphan.update_phantoms(self.view, self.errors[self.view.file_name()], self.view.symbols())

