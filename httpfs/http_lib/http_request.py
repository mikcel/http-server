
__author__ = "Celine Mikiel Yohann"
__id__ = "40009948"

import re
import logging


class HTTPRequest:
    def __init__(self, raw_request_data):

        self.raw_request_data = raw_request_data
        self.method = None
        self.headers = None
        self.http_version = None
        self.uri = None
        self.params = None
        self.empty_request = False
        self.parse_raw_request()

    def parse_raw_request(self):

        # Split the request to seperate headers and body if any
        split_request = self.raw_request_data.split('\r\n')
        if len(split_request) == 0:
            self.empty_request = True
            return

        split_request_header = split_request[0].split(" ")

        self.method = split_request_header[0]
        self.uri = split_request_header[1]
        self.http_version = split_request_header[2].split('/')[1]

        logging.info("Request Method: %s" % self.method)
        logging.info("Request URI: %s" % self.uri)
        logging.info("Request HTTP Version: %s" % self.http_version)

        regexp_header = re.compile(r"^([^:]+):\s?(.+)$", re.IGNORECASE)
        request_headers = dict()

        req_split_idx = 1
        while req_split_idx < len(split_request) and len(split_request[req_split_idx]) > 0 \
                and split_request[req_split_idx]:

            # Split Header key:value
            split_header = list(filter(None, regexp_header.split(split_request[req_split_idx].strip())))

            if len(split_header) == 2:
                request_headers[split_header[0]] = split_header[1]

            req_split_idx += 1

        self.headers = request_headers

        logging.info("Request Headers: %s" % request_headers)

        if req_split_idx < len(split_request) and self.method.upper() == "POST":

            param_list = list()
            for param in split_request[req_split_idx + 1:]:
                param_list.append(param)

            self.params = '\n'.join(param_list)

            logging.info("Request Params: %s" % self.params)
