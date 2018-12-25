import sublime
import sublime_plugin

class TexcuiteSetBibstyleCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._selections = ['IEEEtran', 'alpha', 'geralpha']
    def run(self):
        self.window.show_quick_panel(self._selections, self._handle_stylechange)

    def _handle_stylechange(self, selection):
        print(self._selections[selection])
        project_data = self.window.project_data()
        if "settings" in project_data:
            project_data["settings"]["bibstyle"] = self._selections[selection]
        else:
            project_data["settings"] = {}
        self.window.set_project_data(project_data)

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