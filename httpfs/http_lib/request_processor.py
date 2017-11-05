import mimetypes
import os
import re
import logging
import traceback

from httpfs.http_lib.exceptions import *
from httpfs.http_lib.http_response import HTTPResponse

DEFAULT_WORKING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                   "working_dir")


class RequestProcessor:

    opened_files = list()

    def __init__(self, request, working_dir):
        self.request = request
        self.working_dir = working_dir if not working_dir else DEFAULT_WORKING_DIR

    def process_request(self):

        try:
            self.validate_request()
        except RestrictedAccessError as e:
            return HTTPResponse(status_code=403, body=str(e))
        except Exception as e:
            return HTTPResponse(status_code=400, body=str(e), content_type="text/plain")

        response = None
        if self.request.method is not None:

            if self.request.method.upper() == "GET":

                try:
                    response_body = self.__process_get_request()
                except BadRequestError as e:
                    response_data = self.format_response_dict(status_code=400, body=e)
                except ConflictError as e:
                    response_data = self.format_response_dict(status_code=409, body=e)
                except FileNotFoundError as e:
                    response_data = self.format_response_dict(status_code=404, body=e)
                except (Exception, IOError) as e:
                    traceback.print_exc()
                    response_data = self.format_response_dict(status_code=500, body=e)
                else:
                    response_data = self.format_response_dict(status_code=200, body=response_body["body"],
                                                              content_type=self.get_uri_mime_type(),
                                                              file_name=response_body["file_name"],
                                                              exception=False)

                response = HTTPResponse(status_code=response_data["status_code"],
                                        body=response_data["body"],
                                        content_type=response_data["content_type"],
                                        file_name=response_data["file_name"])

            elif self.request.method.upper() == "POST":

                try:
                    self.__process_post_request()
                except BadRequestError as e:
                    response_data = self.format_response_dict(status_code=400, body=e)
                except ConflictError as e:
                    response_data = self.format_response_dict(status_code=409, body=e)
                except FileNotFoundError as e:
                    response_data = self.format_response_dict(status_code=404, body=e)
                except (Exception, IOError) as e:
                    traceback.print_exc()
                    response_data = self.format_response_dict(status_code=500, body=e)
                else:
                    response_data = self.format_response_dict(status_code=200, body=self.request.params,
                                                              exception=False)

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

        return_data = {"body": None, "file_name": ""}
        requested_file_path = self.working_dir + self.request.uri

        # Handling GET /
        if re.search(r'^\/(\?)?$', self.request.uri) is not None:
            return_data["body"] = self.list_file_dir(self.working_dir)

        # Handling GET /(?)/ -- List sub directories file
        elif re.search(r'^\/.+\/$', self.request.uri) is not None:
            return_data["body"] = self.list_file_dir(requested_file_path)

        # Handling GET /(?)
        elif re.search(r'^\/.+[^/]$', self.request.uri) is not None:

            try:
                self.check_file_lock(requested_file_path)
                logging.info("Opened files: %s" % str(RequestProcessor.opened_files))

                file_data = []
                with open(requested_file_path, "r") as requested_file:
                    self.add_to_opened_file(requested_file_path)
                    for line in requested_file:
                        file_data.append(line)

                file_data = '\n'.join(file_data)

                return_data["body"] = file_data
                return_data["file_name"] = os.path.basename(requested_file_path)

            except FileNotFoundError:
                raise FileNotFoundError("Requested File not found")
            except IOError:
                raise IOError("Error opening requested file")
            finally:
                self.rm_to_opened_file(requested_file_path)

        else:
            raise BadRequestError()

        return return_data

    def __process_post_request(self):

        if re.search(r'^\/.+[^/]$', self.request.uri) is not None:
            requested_file_path = self.working_dir + self.request.uri

            try:

                self.check_file_lock(requested_file_path)
                logging.info("Opened files: %s" % str(RequestProcessor.opened_files))

                with open(requested_file_path, "w") as file_obj:
                    self.add_to_opened_file(requested_file_path)

                    file_obj.write(self.request.params)

                self.rm_to_opened_file(requested_file_path)

            except FileNotFoundError:
                raise FileNotFoundError("Requested file not found")
            except IOError:
                raise IOError("Error writing to file")

        else:
            raise BadRequestError()

    def get_uri_mime_type(self):

        if re.search(r'^\/.+[^/]$', self.request.uri) is not None:
            return mimetypes.guess_type(self.working_dir + self.request.uri)[0]

        return "text/plain"

    @staticmethod
    def check_file_lock(file_path):

        if file_path in RequestProcessor.opened_files:
            raise ConflictError()

        return True

    @staticmethod
    def add_to_opened_file(file_path):
        RequestProcessor.opened_files.append(file_path)

    @staticmethod
    def rm_to_opened_file(file_path):
        if file_path in RequestProcessor.opened_files:
            RequestProcessor.opened_files.remove(file_path)

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

    @staticmethod
    def format_response_dict(status_code=200, body=None, content_type="text/plain", file_name="", exception=True):

        response_dict = dict()

        response_dict["status_code"] = status_code
        response_dict["body"] = str(body)
        response_dict["content_type"] = content_type
        response_dict["file_name"] = file_name

        if exception:
            logging.error(body)

        return response_dict
