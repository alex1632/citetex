import sublime
import sublime_plugin

class TexPhantomManager:
    def __init__(self):
        self._phantoms = list()
        self._phantomset = dict()


    def update_phantoms(self, view, bibentries):
        keys = list()
        self._phantoms = list()
        self._phantomset.update(self._phantoms)
        regions = view.find_all(r"\\cite(?:\[.*?\])?{(.*?)}", 0, "$1", extractions=keys)
        print(keys, regions)

        if view.id() not in self._phantomset:
            self._phantomset[view.id()] = sublime.PhantomSet(view, 'texphantoms')

        for key, region in zip(keys, regions):
            for bfile in bibentries:
                if key in bibentries[bfile]:
                    title = bibentries[bfile][key]["title"][:40]
                    if len(title) == 40:
                        title += "..."
                    phantom_content = """<div style="color: #666">({1}: {0})</div>""".format(title, bibentries[bfile][key]["ref"])
                    # bring phantoms to the back
                    region.a = region.b
                    region.b += 1
                    self._phantoms.append(sublime.Phantom(region, phantom_content, sublime.LAYOUT_INLINE))
                    break


        self._phantomset[view.id()].update(self._phantoms)


    def clear_phantoms(self):
        self._phantoms = list()
        for view in self._phantomset:
            self._phantomset[view.id()].update(self._phantoms)
