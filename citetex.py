from threading import Lock
import sublime
import sublime_plugin
import subprocess
import os
from . import bibmanager
from . import bibphantoms
from . import texcitephantoms as texphantoms

def plugin_loaded():
    try:
        os.makedirs(os.path.join(sublime.cache_path(), "citetex"))
    except OSError:
        pass

    HoverCite.bibman.set_cache_path(os.path.join(sublime.cache_path(), "citetex"))
    print("CiteTex loaded")


class HoverCite(sublime_plugin.ViewEventListener):
    # these cannot be per-instance since focusing on file load would not work.
    bibman = bibmanager.BibManager()
    bibphan = bibphantoms.BibPhantomManager()
    tex_phan = texphantoms.TexPhantomManager()
    current_properties = dict()
    current_path = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = dict()

        self._user_settings = None
        self._default_settings = None
        HoverCite.bibman.set_style("alpha")

    def use_settings(self):
        self._user_settings = sublime.load_settings("CiteTeX-user.sublime-settings")
        self._default_settings = sublime.load_settings("CiteTeX-default.sublime-settings")


    def on_hover(self, point, hover_zone):
        scopes = self.view.scope_name(point).split()
        if 'text.tex.latex' in scopes and 'constant.other.citation.latex' in scopes:
            # print(self.view.substr(self.view.expand_by_class(point, sublime.CLASS_WORD_END | sublime.CLASS_WORD_START, '\{\},')))
            cite_key = self.view.substr(self.view.expand_by_class(point, sublime.CLASS_WORD_END | sublime.CLASS_WORD_START, '\{\},'))
            image_path, HoverCite.current_properties = HoverCite.bibman.serve_entry(cite_key)
            print(image_path)
            info_content = ""
            if "ref" in HoverCite.current_properties:
                info_content += "<h3>[{}]</h3>\n".format(HoverCite.current_properties["ref"])
            if image_path:
                info_content += """<p><img src="file://{}"></p>\n""".format(image_path)

            info_content += """<a href="gotobib">BibTeX entry</a>"""

            if "url" in HoverCite.current_properties:
                info_content += """ | <a href="viewurl">View URL</a>"""

            if "doi" in HoverCite.current_properties:
                info_content += """ | <a href="viewdoi">View DOI</a>"""

            if "resource" in HoverCite.current_properties:
                info_content += """ | <a href="viewres">View Resource ({})</a>""".format(HoverCite.current_properties['resource_type'])

            self.view.show_popup(info_content, sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, max_width=800, on_navigate=self.handle_popup)

    def handle_popup(self, command):
        self.use_settings()
        webbrowser_cmd = self._user_settings.get("webbrowser", self._default_settings.get("webbrowser"))
        if command == "gotobib":
            bib_view = self.view.window().open_file(HoverCite.current_properties["bibfile"])
            marker = next(filter(lambda x: x[1] == HoverCite.current_properties['key'], bib_view.symbols()), None)[0]
            bib_view.show_at_center(marker)

        elif command == "viewurl":
            url = HoverCite.current_properties["url"]
            subprocess.Popen("{} {}".format(webbrowser_cmd, url), shell=True)

        elif command == "viewdoi":
            url = "http://dx.doi.org/" + HoverCite.current_properties["doi"]
            subprocess.Popen("{} {}".format(webbrowser_cmd, url), shell=True)

        elif command == "viewres":
            settings_property = "open_resource_{}".format(HoverCite.current_properties['resource_type'].lower())
            resource_dir = self.view.window().project_data() or {}
            if "settings" in resource_dir and "resource_root" in resource_dir['settings']:
                filepath = os.path.join(resource_dir['settings']['resource_root'], HoverCite.current_properties['resource'])
                open_command = [self._user_settings.get(settings_property, self._default_settings.get(settings_property)), filepath]
                if sublime.platform() == 'windows':
                    subprocess.Popen(open_command, shell=True)
                else:
                    subprocess.Popen(" ".join(open_command), shell=True)


    def on_activated_async(self):
        file_name = self.view.file_name()
        path_of_file = os.path.dirname(file_name) if file_name else None
        scope = self.view.scope_name(0)
        if self.view.file_name() is not None and ("text.tex.latex" in scope.split() or self.view.file_name().endswith('.bib')):
            self.use_settings() # since we use settings, reload them
            if path_of_file != HoverCite.current_path: # if working directory has changed, reload bibfile and error phantoms
                self.view.window().status_message("Load references...")
                HoverCite.current_path = path_of_file
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
                self.view.window().status_message("Cite references loaded.")

            if self.view.file_name().endswith('.tex'): # always refresh title phantoms in tex files
                self.refresh_tex_phantoms()

    def on_post_save_async(self):
        self.use_settings()
        if self.view.file_name().endswith('.bib'):
            if self._user_settings.get("bib_errors", self._default_settings.get("bib_errors")):
                self.errors = HoverCite.bibman.refresh_all_entries(self.view.window().project_data(), self.view.file_name())
                HoverCite.bibphan.update_phantoms(self.view, self.errors[self.view.file_name()], self.view.symbols())

        elif self.view.file_name().endswith('.tex'):
            if self._user_settings.get("tex_phantoms", self._default_settings.get("tex_phantoms")):
                self.refresh_tex_phantoms()

    def refresh_tex_phantoms(self):
        if self._user_settings.get("tex_phantoms", self._default_settings.get("tex_phantoms")):
            HoverCite.tex_phan.update_phantoms(self.view, HoverCite.bibman.bib_entries)
        else:
            HoverCite.tex_phan.clear_phantoms()


    def on_post_text_command(self, command_name, args):
        # used if settings change
        if command_name == "citetex_toggle_tex_phantoms":
            self.use_settings()
            self.refresh_tex_phantoms()
