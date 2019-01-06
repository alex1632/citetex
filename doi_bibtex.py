import sublime
import sublime_plugin
import urllib
import os
import time

from .utils import find_bibfiles

pending_callbacks = dict()

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

        # run DOI get asynchronously
        sublime.set_timeout_async(lambda: self.view.window().run_command("texcuite_fetch_doi", {"doi": doi, "buffer_name": self.view.file_name()}), 0)

class TexcuiteFetchDoi(sublime_plugin.WindowCommand):
    def run(self, doi, buffer_name):
        self._get_doi(doi, buffer_name)
        print("DOI is:" + doi)

    def _get_doi(self, link, buffer_name):
        conn = urllib.request.Request(link, headers={"Accept": "text/x-bibliography; style=bibtex"})
        response = urllib.request.urlopen(conn)
        bibtexentry = response.read().decode('utf-8')

        # detect bibtex key, check for duplicates

        bibfiles = find_bibfiles(buffer_name)
        if bibfiles:
            bibfile = self.window.open_file(bibfiles[0])
            if not bibfile.is_loading():
                bibfile.run_command("texcuite_insert_bibtex", {"entry": bibtexentry})

            global pending_callbacks
            pending_callbacks[bibfiles[0]] = {"entry": bibtexentry}


class TexcuiteInsertBibtex(sublime_plugin.TextCommand):
    def run(self, edit, entry):
        new_entry = "\n" + entry.replace('}, ', '},\n\t')
        pos = self.view.size()
        self.view.insert(edit, pos, new_entry)
        self.view.show(pos)



class DoiEventListener(sublime_plugin.ViewEventListener):

    def on_load(self):
        global pending_callbacks
        if self.view.file_name() in pending_callbacks:
            print("Handle DOI II")
            self._handle_doi(self.view.file_name())

    def _handle_doi(self, file_name):
        print("Processing callback for" + file_name)

        self.view.run_command("texcuite_insert_bibtex", {"entry": pending_callbacks[file_name]["entry"]})

        del pending_callbacks[file_name]

    # curl -LH "Accept: text/x-bibliography; style=bibtex" https://doi.org/10.1126/science.169.3946.635