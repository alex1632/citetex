import re

class BBLParser:
    def __init__(self):
        self.entry_re = re.compile(r"\\bibitem(?:\[((?:[\w\-_{}]|{\\etalchar{\+}})+)\])?\{(.+)\}")

    def parse_bbl(self, inputstr):
        lines = inputstr.split('\n')
        entries = dict()
        suppressors = ['\\BIBentrySTDinterwordspacing', '\\BIBentryALTinterwordspacing']
        current_entry = ""
        for line in lines:
            entry_start = self.entry_re.match(line)
            if entry_start:
                current_entry = entry_start.groups()[1]
                entries[current_entry] = dict()
                entries[current_entry]['block'] = ""
                if entry_start.groups()[0] is not None:
                    entries[current_entry]['ref'] = entry_start.groups()[0].replace('{\\etalchar{+}}', '+').replace('{', '').replace('}', '')

            elif line in suppressors:
                continue

            elif entries:
                entries[current_entry]['block'] += line + '\n'

        return entries




