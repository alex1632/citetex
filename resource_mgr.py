import os
import sublime
import sublime_plugin
from . import citetex

class CitetexAddResource(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bib_entry_list = list()
        self._res_file_list = list()
        self.res_folder = None
    def run(self, edit):
        if self.view.file_name() in citetex.HoverCite.bibman.bib_entries:
            self._bib_entry_list = list(citetex.HoverCite.bibman.bib_entries[self.view.file_name()].keys())
            #zip creates tuples, we wnt a list of lists
            menuentries = [list(y) for y in list(zip([citetex.HoverCite.bibman.bib_entries[self.view.file_name()][x]['title'] for x in self._bib_entry_list], self._bib_entry_list))]
            self.view.window().show_quick_panel(menuentries, self._list_files)
        else:
            self.view.window().status_message("Please open the bibfile you want to insert resources in.")

    def _list_files(self, index):
        proj_settings = self.view.window().project_data() or {}
        if "settings" in proj_settings and "resource_root" in proj_settings['settings'] and index != -1:
            self.res_folder = proj_settings['settings']['resource_root']
            self.current_entry = self._bib_entry_list[index]
            self._res_file_list = [x for x in os.listdir(self.res_folder) if os.path.isfile(os.path.join(self.res_folder, x))]
            print(self._res_file_list)
            self.view.window().show_quick_panel(self._res_file_list, self._insert_entry)

    def _insert_entry(self, index):
        if index != -1:
            new_entry = "\n--resource{{{res}}}{{{typ}}} {name}".format(res=self.current_entry, typ=self._res_file_list[index][-3:].upper(), name = self._res_file_list[index])
            self.view.run_command("citetex_insert_resource_text", {"entry": new_entry})
            

class CitetexInsertResourceText(sublime_plugin.TextCommand):
    def run(self, edit, entry):
        pos = self.view.size()
        self.view.insert(edit, pos, entry)
        self.view.show(pos)
