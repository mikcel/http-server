import socket
import threading
from datetime import datetime

from httpfs.http_lib.request_processor import RequestProcessor
from httpfs.http_lib.http_request import HTTPRequest


class SocketServer(object):

    def __init__(self, host, port, working_dir, debug=False):
        self.host = host
        self.port = port
        self.working_dir = working_dir
        self.debug = debug
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

        request_data = list()

        if self.debug:
            print("\nNew request from %s" % str(addr))

        while True:
            try:
                received_data = conn.recv(2048)
            except socket.timeout:
                print("Unable to read request from client. Timed out.")
                break

            if not received_data:
                break
            else:
                request_data.append(received_data.decode())

            request_data = ''.join(request_data)

            if self.debug:
                print("====PARSING REQUEST====")

            request = HTTPRequest(raw_request_data=request_data, debug=self.debug)

            if self.debug:
                print("====PROCESSING REQUEST====")

            response = RequestProcessor(request=request, working_dir=self.working_dir).process_request()

            if self.debug:
                print("====SENDING RESPONSE====")
            else:
                date_time_now = datetime.now().strftime("%d/%b/%Y %H:%M:%S")
                print("[%s] %s %s from: %s" % (date_time_now, request.method, response.status_code, str(addr)))

            conn.sendall(response.construct_response(debug=self.debug))

            conn.close()

            return
