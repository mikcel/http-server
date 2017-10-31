import mimetypes
import os
import re

from httpfs.http_lib.http_response import HTTPResponse, ContentType

from httpfs.http_lib.exceptions import *

DEFAULT_WORKING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "working_dir")


class RequestProcessor:
    def __init__(self, request, working_dir):
        self.request = request
        self.working_dir = working_dir if not working_dir else DEFAULT_WORKING_DIR

    def process_request(self):

        try:
            self.validate_request()
        except RestrictedAccessError as e:
            return HTTPResponse(status_code=403, body=str(e))
        except Exception as e:
            return HTTPResponse(status_code=400, body=str(e), content_type=ContentType.PLAIN)

        response = None
        if self.request.method is not None:

            if self.request.method.upper() == "GET":

                response_data = {"status_code": 200, "body": "", "content_type": ContentType.PLAIN}
                try:
                    response_body = self.__process_get_request()
                except BadRequestError as e:
                    response_data["status_code"] = 400
                    response_data["body"] = str(e)
                except FileNotFoundError as e:
                    response_data["status_code"] = 404
                    response_data["body"] = str(e)
                except (Exception, IOError) as e:
                    response_data["status_code"] = 500
                    response_data["body"] = str(e)
                else:
                    response_data["body"] = response_body
                    response_data["content_type"] = self.get_uri_mime_type()

                response = HTTPResponse(status_code=response_data["status_code"],
                                        body=response_data["body"],
                                        content_type=response_data["content_type"])

            elif self.request.method.upper() == "POST":

                response_data = {"status_code": 200, "body": "", "content_type": ContentType.PLAIN}
                try:
                    self.__process_post_request()
                except BadRequestError as e:
                    response_data["status_code"] = 400
                    response_data["body"] = str(e)
                except FileNotFoundError as e:
                    response_data["status_code"] = 404
                    response_data["body"] = str(e)
                except (Exception, IOError) as e:
                    response_data["status_code"] = 500
                    response_data["body"] = str(e)

                response = HTTPResponse(status_code=response_data["status_code"],
                                        body=response_data["body"],
                                        content_type=response_data["content_type"])

        else:
            response = HTTPResponse(status_code=400)

        return response

    def validate_request(self):

        if self.request.headers is None or len(self.request.headers) == 0:
            raise Exception("No headers passed!")

        check_req_host = self.request.headers.get("Host")
        if check_req_host is None:
            raise Exception("Unknown Host. Please try again!")

        self.validate_uri()

    def validate_uri(self):

        if self.request.uri is None or self.request.uri == "":
            raise Exception("Empty URI. Please enter a correct URI")

        requested_uri = self.working_dir + self.request.uri

        # Preventing directory traversal attack
        if os.path.realpath(
                os.path.commonprefix((os.path.realpath(requested_uri), self.working_dir))) != self.working_dir:
            raise RestrictedAccessError()

    def __process_get_request(self):

        # Handling GET /
        if re.search(r'^\/(\?)?$', self.request.uri) is not None:
            return self.list_file_dir(self.working_dir)

        requested_file_path = self.working_dir + self.request.uri

        # Handling GET /(?)/ -- List sub directories file
        if re.search(r'^\/.+\/$', self.request.uri) is not None:
            return self.list_file_dir(requested_file_path)

        # Handling GET /(?)
        elif re.search(r'^\/.+[^/]$', self.request.uri) is not None:

            try:
                with open(requested_file_path, "r") as requested_file_obj:
                    return requested_file_obj.read()
            except FileNotFoundError:
                raise FileNotFoundError("Requested File not found")
            except IOError:
                raise IOError("Error opening requested file")

        else:
            raise BadRequestError()

    def __process_post_request(self):

        if re.search(r'^\/.+[^/]$', self.request.uri) is not None:
            requested_file_path = self.working_dir + self.request.uri

            try:
                with open(requested_file_path, "w") as file_obj:
                    file_obj.write(self.request.params)
            except FileNotFoundError:
                raise FileNotFoundError("Requested file not found")
            except IOError:
                raise IOError("Error writing to file")

        else:
            raise BadRequestError()


    def get_uri_mime_type(self):

        if re.search(r'^\/.+[^/]$', self.request.uri) is not None:
            return mimetypes.guess_type(self.working_dir + self.request.uri)[0]

        return ContentType.PLAIN

    @staticmethod
    def list_file_dir(path):

        try:
            dir_list_file = os.listdir(path)
        except FileNotFoundError:
            raise FileNotFoundError("Incorrect URI")
        except:
            raise Exception("Unable to list files in directory")
        else:
            return ", ".join(dir_list_file)

