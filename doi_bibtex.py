import sublime
import sublime_plugin
import urllib

from .utils import find_bibfiles

class TexcuiteDoiToBibtexCommand(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def run(self, edit):
        self.view.window().show_input_panel("Enter DOI: ", "", self._handle_doi, None, None)

    def _handle_doi(self, link):
        if not link.startswith("https://doi.org/"):
            doi = "https://doi.org/" + link
        else:
            doi = link

        sublime.set_timeout_async(lambda: self.view.window().run_command("texcuite_fetch_doi", {"doi": doi, "buffer": self.view.file_name()}), 0)

class TexcuiteFetchDoi(sublime_plugin.WindowCommand):
    def run(self, doi, buffer):
        self._get_doi(doi)
        print("DOI is:" + doi)

    def _get_doi(self, link):
        conn = urllib.request.Request(link, headers={"Accept": "text/x-bibliography; style=bibtex"})
        response = urllib.request.urlopen(conn)
        bibtexentry = response.read()
        print(bibtexentry)

    # curl -LH "Accept: text/x-bibliography; style=bibtex" https://doi.org/10.1126/science.169.3946.635