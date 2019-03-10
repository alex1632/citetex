import sublime
import sublime_plugin
import html

class BibPhantomManager:
    def __init__(self):
        self._phantomset = None
        self._phantoms = list()
        self.stylesheet = '''
            <style>
                div {
                    border-radius: 0.3rem
                }
                div.error {
                    padding: 0.4rem 0.4rem 0.4rem 0.4rem;
                }
                div.warning {
                    padding: 0.4rem 0.4rem 0.4rem 0.4rem;
                }

                a {
                    text-decoration: inherit;
                }
            </style>'''

    def update_phantoms(self, view, errors, regions):
        del self._phantomset
        self._phantomset = sublime.PhantomSet(view, 'bib_error_phantoms')
        self._phantoms = list()
        for err in errors:
            # print(err)
            if "entry" in err:
                region = view.expand_by_class(next(filter(lambda x: x[1] == err['entry'], regions), None)[0], sublime.CLASS_LINE_START)
            elif "line" in err:
                region = view.expand_by_class(view.line(view.text_point(err['line'], 0)), sublime.CLASS_LINE_START)

            if region:
                if err['level'] == "WARN":
                    error_content = '<body>' + self.stylesheet + \
                                '<div class="warning">' +  html.escape(err['type'], quote=False) + ' ' + \
                                '<a href=hide>(Close all)</a></div>' + \
                                '</body>'
                elif err['level'] == "ERROR":
                    error_content = '<body>' + self.stylesheet + \
                                '<div class="error">' + html.escape(err['type'], quote=False) + " " + \
                                '<a href=hide>(Close all)</a></div>' + \
                                '</body>'
                self._phantoms.append(sublime.Phantom(region, error_content, sublime.LAYOUT_BELOW, self._handle_phantom_link))

        self._phantomset.update(self._phantoms)


    def _handle_phantom_link(self, href):
        if href == "hide":
            self.clear_phantoms()

    def clear_phantoms(self):
        self._phantoms = list()
        if self._phantomset:
            self._phantomset.update(self._phantoms)

