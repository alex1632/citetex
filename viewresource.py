import sublime
import sublime_plugin
import os
from .citetex import HoverCite
from .utils import process_open

class CitetexViewResourcePdf(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entries = list()
        self._user_settings = sublime.load_settings("CiteTeX-user.sublime-settings")
        self._default_settings = sublime.load_settings("CiteTeX-default.sublime-settings")


    def run(self, edit):
        all_res = HoverCite.bibman.bib_entries
        for filen in all_res:
            res = all_res[filen]
            self.entries = [res[x] for x in res if 'resource_type' in res[x] and res[x]['resource_type'] == 'PDF']

        # menu_select = [["[{}] - {}".format(x['ref'], x['title']), "{}".format(x['resource'])] for x in self.entries]
        menu_select = [["{} {} - {}".format(x['author'], x['year'], x['title']), "{}".format(x['resource'])] for x in self.entries]
        # print(self.entries)
        self.view.window().show_quick_panel(menu_select, self.handle_cb)

    def handle_cb(self, idx):
        if idx >= 0:
            settings_property = "open_resource_{}".format(self.entries[idx]['resource_type'].lower())
            resource_dir = self.view.window().project_data() or {}
            if "settings" in resource_dir and "resource_root" in resource_dir['settings']:
                filepath = os.path.join(resource_dir['settings']['resource_root'], self.entries[idx]['resource'])
                open_command = [self._user_settings.get(settings_property, self._default_settings.get(settings_property)), filepath]
                process_open(open_command)
