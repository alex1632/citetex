import re

class BibParser:
    def __init__(self):
        self._type_key_re = re.compile(r"\s*@(.*?){(.*),")
        self._bibentry_type_re = re.compile(r"\s*(\w+)\s*=\s*(?:{|\")(.*)(?:}|\").*")
        self._comment_file_re = re.compile(r"@Comment\s*sublime-resource{(.*)}{(PDF)} (.*)")

    def parse_bibfile(self, bibfile):
        # os.path.dirname(bibfile)
        data = dict()
        with open(bibfile, "r", encoding="utf-8") as bfile:
            content = bfile.read().split('\n')
            current_key = None

            for entry in content:
                match = self._type_key_re.match(entry)
                if match:
                    groups = match.groups()
                    current_key = groups[1]
                    data[current_key] = dict()
                    data[current_key]["type"] = groups[0]
                    continue

                match = self._bibentry_type_re.match(entry)
                if match:
                    groups = match.groups()
                    group_type = groups[0].lower()
                    if group_type == "url" or group_type == "doi" or group_type == "year":
                        data[current_key][group_type] = groups[1]
                    elif (group_type == "title" or group_type == "booktitle") and 'title' not in data[current_key]:
                        data[current_key]["title"] = groups[1].replace('{', '').replace('}', '')

                    continue

                match = self._comment_file_re.match(entry)
                if match:
                    groups = match.groups()
                    data[groups[0]]['resource'] = groups[2]
                    data[groups[0]]['resource_type'] = groups[1]
        return data


