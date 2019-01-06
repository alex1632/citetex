import sublime
import sublime_plugin

class TexcuiteSetBibstyleCommand(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._selections = ['IEEEtran', 'alpha', 'geralpha']
    def run(self, edit):
        self.view.window().show_quick_panel(self._selections, self._handle_stylechange)

    def _handle_stylechange(self, selection):
        project_data = self.view.window().project_data() or {}


        if "settings" not in project_data:
            project_data["settings"] = {}

        project_data["settings"]["bibstyle"] = self._selections[selection]

        self.view.window().set_project_data(project_data)
        # print(self._selections[selection])

class TexcuiteHandleConfigCommand(sublime_plugin.ApplicationCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_settings = sublime.load_settings("TeXCuite-user.sublime-settings")

    def load_settings(self):
        self._user_settings = sublime.load_settings("TeXCuite-user.sublime-settings")

    def save_settings(self):
        sublime.save_settings("TeXCuite-user.sublime-settings")

    def run(self, entry, param):
        print(entry, param)
        self.load_settings()
        self._user_settings.set(entry, param)
        self.save_settings()