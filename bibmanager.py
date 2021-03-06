import sublime
import os
from . import tex_interface
from . import bblparser
from . import bibparser
from .utils import find_bibfiles

class BibManager:
    def __init__(self):
        self.style = "IEEEtran"
        self.bib_entries = dict()
        self.cwd = None
        self.tex_interface = tex_interface.TeXRenderer()
        self.bblparser = bblparser.BBLParser()
        self.bibparser = bibparser.BibParser()

    def set_cache_path(self, cwd):
        self.cwd = cwd
        self.tex_interface.set_cache_path(cwd)

    def set_style(self, style):
        self.style = style

    def detect_environment(self, project_data, buffer_name):
        bibfiles = None
        if buffer_name: # file exists on disk
            env = os.path.dirname(buffer_name)
        else:
            return None # we shouldn't end up here

        if project_data: # Sublime window has active project file
            if "texcite" in project_data:
                bibfiles = project_data["texcite"]["bibfiles"] if "bibfiles" in project_data["texcite"] else None

        if not bibfiles:
            bibfiles = find_bibfiles(buffer_name)

            print("bibfiles: " + str(bibfiles))
        return bibfiles


    def reload_bibfile(self, bibfile):
        bblfile, errors = self.tex_interface.generate_bbl(self.style, bibfile)

        if os.path.exists(bblfile):
            self.bib_entries[bibfile] = self.bibparser.parse_bibfile(bibfile)
            with open(bblfile, "r", encoding="utf-8") as bbl:
                content = bbl.read()
                bbl_info = self.bblparser.parse_bbl(content)
                for key in self.bib_entries[bibfile]:
                    self.bib_entries[bibfile][key].update(bbl_info[key])

        return errors

    def refresh_all_entries(self, project_data, buffer_name):
        errors = dict()
        self.bib_entries = dict()
        bibfiles = self.detect_environment(project_data, buffer_name)

        for bibfile in bibfiles:
            err = self.reload_bibfile(bibfile)
            errors[bibfile] = err

        return errors

    def serve_entry(self, key, render=True):
        properties = dict()
        image_path = None
        for bib in self.bib_entries:
            if key in self.bib_entries[bib]:
                if render:
                    image_path = self.tex_interface.render_tex(self.bib_entries[bib][key]['block'], 150)
                properties = self.bib_entries[bib][key]
                properties["key"] = key
                properties["bibfile"] = bib
                break

        return image_path, properties


