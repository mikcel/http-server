import re


class HTTPRequest:
    def __init__(self, raw_request_data, debug=False):

        self.raw_request_data = raw_request_data
        self.method = None
        self.headers = None
        self.http_version = None
        self.uri = None
        self.params = None
        self.empty_request = False
        self.debug = debug
        self.parse_raw_request()

    def parse_raw_request(self):

        split_request = self.raw_request_data.split('\r\n')
        if len(split_request) == 0:
            self.empty_request = True
            return

        split_request_header = split_request[0].split(" ")

        self.method = split_request_header[0]
        self.uri = split_request_header[1]
        self.http_version = split_request_header[2].split('/')[1]

        if self.debug:
            print("Request Method: %s" % self.method)
            print("Request URI: %s" % self.uri)
            print("Request HTTP Version: %s" % self.http_version)

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

        if self.debug:
            print("Request Headers: %s" % request_headers)

        if req_split_idx < len(split_request) and self.method.upper() == "POST":

            param_list = list()
            for param in split_request[req_split_idx + 1:]:
                param_list.append(param)

            self.params = '\n'.join(param_list)

            if self.debug:
                print("Request Params: %s" % self.params)
