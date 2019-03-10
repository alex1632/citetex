import re

class BibParser:
    def __init__(self):
        self._type_key_re = re.compile(r"\s*@(\w*){(.*),")
        self._bibentry_type_re = re.compile(r"\s*(\w+)=(?:{|\")(.*)(?:}|\").*")
        self._comment_file_re = re.compile(r"--resource{(.*)}{(.*)}")

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
                    if groups[0] == "url" or groups[0] == "DOI" or groups[0] == "year":
                        data[current_key][groups[0]] = groups[1]
                    elif groups[0] == "title" or groups[0] == "booktitle":
                        data[current_key]["title"] = groups[1].replace('{', '').replace('}', '')

                    continue

                match = self._comment_file_re.match(entry)
                if match:
                    data[current_key]['resources'] = match.groups()[1]

        print(data)

        return data


