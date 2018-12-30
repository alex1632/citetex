import os
import re

class ReferenceFinder:
    def __init__(self):
        self.entries = list()
        self.rootdir = None
        self._titles_re = re.compile(r"\s*\\((?:sub){,2})(part|section|chapter|(?:foot)?caption)(?:\[.*\])?{(.*)}")
        self._scope_re = re.compile(r"\s*\\(begin|end){(figure|table|equation)}")
        self._label_re = re.compile(r"\s*\\label{(.*)}")
        self._listing_re = re.compile(r"(?:.*?(caption|label)=(.*?)(?:,|\]))")

    def update_references(self, rootdir):
        self.rootdir = rootdir
        self.entries = list()

        for file in os.listdir(self.rootdir):
            if os.path.isfile(os.path.join(self.rootdir, file)) and file.endswith(".tex"):
                self.find_labels(os.path.join(self.rootdir, file))

    def update_file(self, filename):
        self.entries = list(filter(lambda x: x != filename, self.entries))
        self.find_labels(filename)

    def find_labels(self, filename):
        with open(filename, "r", encoding="utf-8") as texfile:
            content = texfile.read().split('\n')

        typ, params, text = None, None, None
        for line in content:
            label = self._label_re.match(line)
            scope = self._scope_re.match(line)
            title = self._titles_re.match(line)
            listing = self._listing_re.findall(line)

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
                self.entries.append({"filename": filename, "type": typ if not None else "", "label": label.groups()[0], "text": text, "params": params})
                typ, params, text = None, None, None

            if listing:
                text = next(filter(lambda x: x[0] == "caption", listing), (None, None))[1]
                label = next(filter(lambda x: x[0] == "label", listing), (None, None))[1]
                self.entries.append({"filename": filename, "type": "listing", "label": label, "text": text, "params": ''})
                typ, params, text = None, None, None


    def deliver_entries(self):
        return [["{}".format(x["text"]), "{} {} - {}".format((x["params"] + x["type"]).title(), x["label"], os.path.basename(x["filename"]))] for x in self.entries]

    def query_entry(self, number, user_settings, default_settings, local_settings):
        entry = self.entries[number]
        config_user = local_settings["settings"]["references"] if \
         "settings" in local_settings and "references" in local_settings["settings"] \
         else user_settings.get("references")
        config_default = default_settings.get("references")

        locale = config_user["locale"] if (config_user is not None and "locale" in config_user) else config_default["locale"]

        try:
            locale_dict = config_user["locales"][locale] if (config_user is not None and "locales" in config_user) else config_default["locales"][locale]

            abbrv = locale_dict[entry["type"]]
            return "{}~\\ref{{{}}} ".format(abbrv, entry["label"])
        except KeyError:
            print("Could not find definition for {} in locale {}".format(entry["type"], locale))

    def query_popup(self, key):
        return next(filter(lambda x: x["label"] == key, self.entries), None)