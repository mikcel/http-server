import traceback
from collections import OrderedDict
from datetime import datetime
from enum import Enum


class ContentType(Enum):
    HTML = 'text/html'
    PLAIN = 'text/plain'
    JSON = 'text/json'


class HTTPResponse:
    def __init__(self, status_code=200, body="", content_type=ContentType.PLAIN, additional_headers=None):

        self.status_code = status_code
        self.content_type = content_type
        self.body = body
        self.additional_headers = additional_headers

    def construct_response(self, debug=False):

        try:
            status_desc = self.map_status_code()

            status_line = "HTTP/1.1 %d %s" % (self.status_code, status_desc)

            if not isinstance(self.content_type, ContentType):
                content_type = self.content_type
            else:
                content_type = self.content_type.value

            headers = OrderedDict(
                [("Date", datetime.now().strftime("%a, %d %b %Y %H:%M:%S %Z")),
                 ("Server", "localhost"),
                 ("Content-Length", len(self.body)),
                 ("Content-Type", content_type),
                 ("Connection", "close")]
            )

            if self.additional_headers is not None and isinstance(self.additional_headers, dict):
                headers.update(self.additional_headers)

            headers_str = ""
            for key, value in headers.items():
                headers_str += "%s: %s\r\n" % (key, value)

            final_response = """%s\r\n%s\r\n%s""" % (status_line, headers_str, self.body)

        except Exception:

            traceback.print_exc()
            final_response = """HTTP/1.1 500 INTERNAL ERROR"""

        if debug:
            print(final_response)

        return final_response.encode("utf-8")

    def map_status_code(self):

        mapping_dict = {
            200: 'OK',
            400: 'Bad Request',
            404: 'Not Found',
            403: 'Forbidden',
            405: 'Method not allowed',
            408: 'Request Time-out',
            411: 'Length Required',
            500: 'Internal Server Error'
        }

        if self.status_code is not None and isinstance(self.status_code, int) and self.status_code in mapping_dict:
            return mapping_dict.get(self.status_code)
        else:
            self.status_code = 500
            return mapping_dict.get(self.status_code)
