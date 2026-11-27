
# This is for Python 3
import html as html_converter

# for Python 2 uncomment this line
#import cgi as html_converter

class UnicodeFileToHtmlTextConverter(object):

    def __init__(self, full_filename_with_path):
        """Store the path of the text file to convert."""
        self.full_filename_with_path = full_filename_with_path

    def convert_to_html(self):
        """Read each line, trim its trailing whitespace, HTML-escape it, and append a line break."""
        f = open(self.full_filename_with_path, "r")
        html = ""
        for line in f:
            line = line.rstrip()
            html += html_converter.escape(line, quote=True)
            html += "<br />"

        return html