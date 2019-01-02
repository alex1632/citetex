import sublime
import sublime_plugin
import subprocess
import os
import re

tex_skeleton = r"""
\documentclass[preview]{{standalone}}
\usepackage{{url}}

\begin{{document}}
{}
\end{{document}}

"""

aux_skeleton = r"""
\relax
\bibstyle{{{style}}}
\bibdata{{{bibl}}}
\citation{{*}}

"""

class TeXRenderer:
    def __init__(self, tex="latex", bibinterface="bibtex", cwd="/tmp"):
        self.texcommand = tex
        self.cwd = cwd
        self.bibinterface = bibinterface
        self.AUXFILE_PREFIX = "cite"
        self._re_bibtex_error = re.compile(r"(.*)---line (\d+) of file (.*)")
        self._re_bibtex_warning1 = re.compile(r"Warning--(.*?) in (.*)")
        self._re_bibtex_warning2 = re.compile(r"Warning--(.*?)\n--line (\d+)", re.MULTILINE)
        self._env = os.environ.copy()
        self._settings = sublime.load_settings("TeXCuite-default.sublime-settings")
        self._settings_u = sublime.load_settings("TeXCuite-user.sublime-settings")
        print(sublime.cache_path())

    def render_tex(self, inputstr, dpi):
        document = tex_skeleton.format(inputstr)
        tex_cmd = subprocess.Popen("{} -jobname cite".format(self.texcommand), cwd=self.cwd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
        tex_cmd.communicate(input=document.encode())
        tex_cmd.wait()
        subprocess.Popen(" ".join(["dvipng", "-D", str(dpi), "-bg Transparent", "-fg White", "cite.dvi"]), cwd=self.cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True).wait()

        return os.path.join(self.cwd, "cite1.png")


    def generate_bbl(self, style, bibfile):
        # BSINPUTS, BIBINPUTS variable!! --> bst files
        self._env["BSTINPUTS"] = os.path.dirname(bibfile)
        bstsettings = self._settings_u.get("bibtex", self._settings.get("bibtex"))
        print("bstsettings:" + str(bstsettings))
        if bstsettings and "bstpath" in bstsettings[sublime.platform()]:
            self._env["BSTINPUTS"] += ";" + bstsettings[sublime.platform()]["bstpath"]

        with open(os.path.join(self.cwd, self.AUXFILE_PREFIX + ".aux"), "w") as caux:
            caux.write(aux_skeleton.format(style=style, bibl=bibfile.rstrip('.bib')))
        bibtex_proc = subprocess.Popen("{} {}".format(self.bibinterface, self.AUXFILE_PREFIX + ".aux"), cwd=self.cwd, shell=True, stdout=subprocess.PIPE, env=self._env)
        bibtex_stdout = bibtex_proc.communicate()
        errors = self.parse_bibtex_errors(bibtex_stdout[0].decode())

        return os.path.join(self.cwd, self.AUXFILE_PREFIX + ".bbl"), errors

    def parse_bibtex_errors(self, bibtex_out):
        errors = list()
        # It seems like error lines have to be divided by 2 in case of errors -- WHY?
        for e in self._re_bibtex_error.findall(bibtex_out):
            errors.append({"level": "ERROR", "line": int(e[1]), "type": e[0], "file": e[2]})

        for w in self._re_bibtex_warning1.findall(bibtex_out):
            errors.append({"level": "WARN", "type": w[0], "entry": w[1]})
        for w in self._re_bibtex_warning2.findall(bibtex_out):
            errors.append({"level": "WARN", "type": w[0], "line": int(w[1])})
        return errors