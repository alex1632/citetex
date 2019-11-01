import os
import re

class ReferenceHandler:
    def __init__(self):
        self.entries = list()
        self.rootdir = None
        self._titles_re = re.compile(r"\s*\\((?:sub){,2})(part|section|chapter|(?:foot)?caption)(?:\[.*\])?{(.*)}")
        self._scope_re = re.compile(r"\s*\\(begin|end){(.*?)}.*")
        self._label_re = re.compile(r".*\\label{(.*)}")
        self._listing_re = re.compile(r"(?:.*?(caption|label)=(.*?)(?:,|\]))")

    def update_references(self, rootdir):
        # called if selected tab belongs to a tex project and the former did not
        self.rootdir = rootdir
        self.entries = list()

        for file in os.listdir(self.rootdir):
            if os.path.isfile(os.path.join(self.rootdir, file)) and file.endswith(".tex"):
                self.find_labels(os.path.join(self.rootdir, file))

    def update_file(self, filename):
        self.entries = list(filter(lambda x: x["filename"] != filename, self.entries))
        self.find_labels(filename)

    def find_labels(self, filename):
        # parse tex scopes such as figure, table...
        with open(filename, "r", encoding="utf-8") as texfile:
            content = texfile.read().split('\n')

        params, text = "", ""
        #handle nested scopes
        typ = list()
        for linenumber, line in enumerate(content):
            label = self._label_re.match(line)
            scope = self._scope_re.match(line)
            title = self._titles_re.match(line)
            listing = self._listing_re.findall(line)

            if scope:
                context = scope.groups()[0]
                proposed_type = scope.groups()[1]
                if context == "begin":
                    typ.append(proposed_type)
                elif context == "end":
                    try:
                        typ.pop(-1) # pop the scope added
                    except IndexError:
                        print("Empty scope {} at: {}:{}".format(context,filename, linenumber))

            elif title:
                text = title.groups()[2]
                # keep type of label if parsed string belongs to a scope (figure)
                if not title.groups()[1] == "caption":
                    typ.append(title.groups()[1])
                params = title.groups()[0]

            if label:
                l = label.groups()
                try:
                    t = typ[-1]
                    self.entries.append({"filename": filename, "type": t, "label": l[0], "text": text if t != "equation" else "{}".format(l[0]), "params": params})
                except IndexError:
                    # print("Empty list at: {} {} {}".format(filename, l[0], text))
                    pass # happens if labels in commented scopes occur

                params, text = "", ""

            if listing:
                text = next(filter(lambda x: x[0] == "caption", listing), (None, None))[1]
                label = next(filter(lambda x: x[0] == "label", listing), (None, None))[1]
                self.entries.append({"filename": filename, "type": "Listing", "label": label, "text": text, "params": ''})
                params, text = "", ""




    def deliver_entries(self):
        return [["{1}:  {0}".format(x["text"], x["type"]).title(), "{} {} - {}".format(x["params"] , x["label"], os.path.basename(x["filename"]))] for x in self.entries]

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
            # print(entry['type'])
            eq_prefix = "eq" if entry['type'] == "equation" else ""
            return "{}~\\{}ref{{{}}}".format(abbrv, eq_prefix, entry["label"])
        except KeyError:
            print("Could not find definition for {} in locale {}".format(entry["type"], locale))
            return "\\ref{{{}}}".format(entry["label"])

    def query_popup(self, key):
        return next(filter(lambda x: x["label"] == key, self.entries), None)
