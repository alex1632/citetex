import sublime
import sublime_plugin
import html

class BibPhantomManager:
    def __init__(self):
        self._phantomset = None
        self._phantoms = list()
        self.stylesheet = '''
            <style>
                div.error {
                    padding: 0.4rem 0 0.4rem 0.7rem;
                    margin: 0 0 0.2rem;
                }

                div.error span.message {
                    padding-right: 0.7rem;
                }

                div.error a {
                    text-decoration: inherit;
                    padding: 0.35rem 0.7rem 0.45rem 0.8rem;
                    position: relative;
                    bottom: 0.05rem;
                    border-radius: 0 0.2rem 0.2rem 0;
                    font-weight: bold;
                }
                html.dark div.error a {
                    background-color: #00000018;
                }
                html.light div.error a {
                    background-color: #ffffff18;
                }
                div.warning {
                    padding: 0.4rem 0 0.4rem 0.7rem;
                    margin: 0 0 0.2rem;
                }

                div.warning span.message {
                    padding-right: 0.7rem;
                }

                div.warning a {
                    text-decoration: inherit;
                    padding: 0.35rem 0.7rem 0.45rem 0.8rem;
                    position: relative;
                    bottom: 0.05rem;
                    border-radius: 0 0.2rem 0.2rem 0;
                    font-weight: bold;
                }
                html.dark div.warning a {
                    background-color: #00000018;
                }
                html.light div.warning a {
                    background-color: #ffffff18;
                }
            </style>
        '''

    def update_phantoms(self, view, errors, regions):
        del self._phantomset
        self._phantomset = sublime.PhantomSet(view, 'bib_error_phantoms')
        self._phantoms = list()
        for error in errors:
            # print(error)
            if "entry" in error:
                region = view.expand_by_class(next(filter(lambda x: x[1] == error['entry'], regions), None)[0], sublime.CLASS_LINE_START)
            elif "line" in error:
                region = view.expand_by_class(view.line(view.text_point(error['line'], 0)), sublime.CLASS_LINE_START)

            if error['level'] == "WARN":
                error_content = '<body id=warning>' + self.stylesheet + \
                            '<div class="warning">' + \
                            '<span class="message">' + html.escape(error['type'], quote=False) + '</span>' + \
                            '<a href=hide>' + chr(0x00D7) + '</a></div>' + \
                            '</body>'
            elif error['level'] == "ERROR":
                error_content = '<body id=error>' + self.stylesheet + \
                            '<div class="error">' + \
                            '<span class="message">' + html.escape(error['type'], quote=False) + '</span>' + \
                            '<a href=hide>' + chr(0x00D7) + '</a></div>' + \
                            '</body>'
            if region:
                self._phantoms.append(sublime.Phantom(region, error_content, sublime.LAYOUT_BELOW, self._handle_phantom_link))

        self._phantomset.update(self._phantoms)


    def _handle_phantom_link(self, href):
        if href == "hide":
            self.clear_phantoms()

    def clear_phantoms(self):
        self._phantoms = list()
        self._phantomset.update(self._phantoms)

