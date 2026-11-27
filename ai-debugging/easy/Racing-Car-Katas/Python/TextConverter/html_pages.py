"""This is a second, slightly harder problem on the same theme as the first."""

# This is for Python 3
import html as html_converter

# for Python 2 uncomment this line
#import cgi as html_converter

class HtmlPagesConverter:

    def __init__(self, filename):
        """Read the file and record zero, page-break, and end-of-file positions for fast page access."""
        self.filename = filename
        self.breaks = [0]
        with open(self.filename, "r", encoding="UTF-8") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                line = line.rstrip()
                if "PAGE_BREAK" in line:
                    page_break_position = f.tell()
                    self.breaks.append(f.tell())
            self.breaks.append(f.tell())                

    def get_html_page(self, page):
        """Return the zero-indexed page as HTML, escaping text and omitting page-break markers."""
        page_start = self.breaks[page]
        page_end = self.breaks[page+1]
        html = ""
        with open(self.filename, "r", encoding="UTF-8") as f:
            f.seek(page_start)
            while f.tell() != page_end:
                line = f.readline()
                line = line.rstrip()
                if "PAGE_BREAK" in line:
                    continue
                html += html_converter.escape(line, quote=True)
                html += "<br />"
        return html

