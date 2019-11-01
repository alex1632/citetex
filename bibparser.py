import re

class BibParser:
    def __init__(self):
        self._type_key_re = re.compile(r"\s*@(.*?){(.*),")
        self._bibentry_type_re = re.compile(r"\s*(\w+)\s*=\s*(?:{|\")((?:.*?(?:{.*?})?)+)(?:}|\"|$).*")
        self._comment_file_re = re.compile(r"%@Comment\s*sublime-resource{(.*)}{(PDF)} (.*)")

    def parse_bibfile(self, bibfile):
        # os.path.dirname(bibfile)
        print("Triggered to parse bibfile {}".format(bibfile))
        data = dict()
        with open(bibfile, "r", encoding="utf-8") as bfile:
            content = bfile.read().split('\n')
            current_key = None
            has_booktitle = False
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
                    if group_type in ["url", "doi", "year", "address"]:
                        data[current_key][group_type] = groups[1]
                    elif group_type == "title" or ((group_type == "booktitle") and 'title' not in data[current_key]):
                        data[current_key]["title"] = groups[1].replace('{', '').replace('}', '')
                    elif group_type == "author":
                        data[current_key]['author'] = groups[1].split(',')[0] # store only first author's last name
                        # data[current_key]['author'] = groups[1].split(' and ')

                    continue

                match = self._comment_file_re.match(entry)
                if match:
                    groups = match.groups()
                    data[groups[0]]['resource'] = groups[2]
                    data[groups[0]]['resource_type'] = groups[1]

        return data


