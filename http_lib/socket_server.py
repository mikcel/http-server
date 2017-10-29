import socket
import threading
import traceback

from http_lib.http_request import HTTPRequest
from http_lib.request_processor import RequestProcessor


class SocketServer(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run_server(self):

        try:
            self.listener.bind((self.host, self.port))

            # no. of unaccepted connections that the system will allow before refusing new connections
            self.listener.listen(5)

            print("HTTP Server is listening at %s" % self.port)
            print("Quit the server with CTRL-BREAK")

            while True:
                conn, addr = self.listener.accept()
                threading.Thread(target=self.__handle_request, args=(conn, addr)).start()

        except InterruptedError:
            print("Interruption error while accepting connection")
        except KeyboardInterrupt:
            print("Exiting server")
        except OSError as e:
            print(e)
        finally:
            self.listener.close()

    def __handle_request(self, conn, addr):

        print("\nNew request from %s" % str(addr))

        while True:
            try:
                request_data = conn.recv(1024)
            except socket.timeout:
                print("Unable to read request from client. Timed out.")
                break

            if not request_data:
                break

            try:
                print("====PARSING REQUEST====")
                request = HTTPRequest(raw_request_data=request_data.decode())

                print("====PROCESSING REQUEST====")
                response = RequestProcessor(request=request).process_request()

                print("====SENDING RESPONSE====")
                conn.send(response.construct_response())

            except Exception as e:
                traceback.print_exc()

            conn.close()

            break
