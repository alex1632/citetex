import os
import re

class ReferenceFinder:
    def __init__(self):
        self.entries = list()
        self.rootdir = None
        self._titles_re = re.compile(r"\\((?:sub){,2})(section|chapter|caption){(.*)}")
        self._scope_re = re.compile(r"\\(begin|end){(figure|table|equation)}")
        self._label_re = re.compile(r"\\label{(.*)}")

    def update_references(self, rootdir):
        self.rootdir = rootdir
        self.entries = list()

        for file in os.listdir(self.rootdir):
            if os.path.isfile(os.path.join(self.rootdir, file)) and file.endswith(".tex"):
                print(self.rootdir, file)
                self.find_labels(os.path.join(self.rootdir, file))


        print(self.entries)

    def find_labels(self, filename):
        print(filename)
        with open(filename, "r") as texfile:
            content = texfile.read().split('\n')

        typ, params, text = None, None, None
        for line in content:
            label = self._label_re.match(line)
            scope = self._scope_re.match(line)
            title = self._titles_re.match(line)

            if scope:
                context = scope.groups()[0]
                if context == "begin":
                    typ = scope.groups()[1]
                else:
                    typ = None

            elif title:
                text = title.groups()[2]
                # keep type of label if parsed string belongs to a scope (figure)
                typ = title.groups()[1] if not title.groups()[1] == "caption" else typ
                params = title.groups()[0]

            elif label:
                self.entries.append({"filename": filename, "type": typ, "label": label.groups()[0], "text": text, "params": params})
                typ, params, text = None, None, None
