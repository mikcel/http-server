
__author__ = "Celine Mikiel Yohann"
__id__ = "40009948"

import logging
import traceback
from collections import OrderedDict
from datetime import datetime


class HTTPResponse:
    def __init__(self, status_code=200, body="", content_type="text/plain", additional_headers=None, file_name=""):

        self.status_code = status_code
        self.content_type = content_type
        self.body = body
        self.additional_headers = additional_headers
        self.file_name = file_name

    def construct_response(self):

        try:
            # Get status code
            status_desc = self.map_status_code()

            # Set status line
            status_line = "HTTP/1.1 %d %s" % (self.status_code, status_desc)

            # Set content disposition if file name exists or if content type is set
            if self.file_name or self.content_type:
                content_disposition = self.determine_disposition()
            else:
                content_disposition = ""

            # Generate headers
            headers = OrderedDict(
                [("Date", datetime.now().strftime("%a, %d %b %Y %H:%M:%S %Z")),
                 ("Server", "localhost"),
                 ("Content-Length", len(self.body)),
                 ("Content-Type", self.content_type),
                 ("Connection", "close")]
            )

            if content_disposition and content_disposition != "":
                headers["Content-Disposition"] = content_disposition

            if self.additional_headers is not None and isinstance(self.additional_headers, dict):
                headers.update(self.additional_headers)

            headers_str = ""
            for key, value in headers.items():
                headers_str += "%s: %s\r\n" % (key, value)

            response_format = """%s\r\n%s\r\n%s"""
            logging.info(response_format % (status_line, headers_str, ""))

            final_response = response_format % (status_line, headers_str, self.body)

        except Exception:

            traceback.print_exc()
            final_response = """HTTP/1.1 500 INTERNAL ERROR"""

            logging.info(final_response)

        return final_response.encode("utf-8")

    def map_status_code(self):

        mapping_dict = {
            200: 'OK',
            400: 'Bad Request',
            404: 'Not Found',
            403: 'Forbidden',
            405: 'Method not allowed',
            409: 'Conflict',
            408: 'Request Time-out',
            411: 'Length Required',
            500: 'Internal Server Error'
        }

        if self.status_code is not None and isinstance(self.status_code, int) and self.status_code in mapping_dict:
            return mapping_dict.get(self.status_code)
        else:
            self.status_code = 500
            return mapping_dict.get(self.status_code)

    def determine_disposition(self):

        if "text" in self.content_type:
            return "inline"
        else:
            return 'attachment; filename="%s"' % self.file_name
