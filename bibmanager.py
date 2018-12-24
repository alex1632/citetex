import os
from . import tex_interface
from . import bblparser

class BibManager:
    def __init__(self, logger):
        self.logger = logger
        self.style = "IEEEtran"
        self.bib_entries = dict()
        self.tex_interface = tex_interface.TeXRenderer(self.logger)
        self.bblparser = bblparser.BBLParser()

    def set_style(self, style):
        self.style = style

    def detect_environment(self, project_data, buffer_name):
        bibfiles = None
        if buffer_name: # file exists on disk
            env = os.path.dirname(buffer_name)
            self.logger.debug("Env is: {}".format(env))
        else:
            return None # we shouldn't end up here

        if project_data: # Sublime window has active project file
            if "texcite" in project_data:
                bibfiles = project_data["texcite"]["bibfiles"] if "bibfiles" in project_data["texcite"] else None

        if not bibfiles:
            candidates = list(filter(lambda x: x.endswith('.bib'), os.listdir(env)))
            if candidates:
                bibfiles = [os.path.join(env, x) for x in candidates]
        self.logger.debug("Bibfile(s) are: {}".format(bibfiles))
        return bibfiles


    def reload_bibfile(self, bibfile):
        bblfile, errors = self.tex_interface.generate_bbl(self.style, bibfile)

        if os.path.exists(bblfile):
            with open(bblfile, "r") as bbl:
                self.bib_entries[os.path.basename(bblfile).rstrip('.bib')] = self.bblparser.parse_bbl(bbl.read())
        else:
            self.logger.info("File {} does not exist!".format(bblfile))

        return errors

    def refresh_all_entries(self, project_data, buffer_name):
        errors = dict()
        self.bib_entries = dict()
        bibfiles = self.detect_environment(project_data, buffer_name)

        for bibfile in bibfiles:
            self.logger.debug("Loading file: {}".format(bibfile))
            err = self.reload_bibfile(bibfile)
            errors[bibfile] = err

        return errors

    def serve_entry(self, key):
        properties = dict()
        image_path = None
        # print(key)
        for bib in self.bib_entries:
            if key in self.bib_entries[bib]:
                image_path = self.tex_interface.render_tex(self.bib_entries[bib][key]['block'], 150)
                if "ref" in self.bib_entries[bib][key]:
                    properties["ref"] = self.bib_entries[bib][key]["ref"]
                break

        # print(image_path)
        return image_path, properties


