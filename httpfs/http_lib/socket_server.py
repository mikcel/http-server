import socket
import threading
import traceback
from datetime import datetime
from time import sleep

from httpfs.http_lib.http_request import HTTPRequest
from httpfs.http_lib.request_processor import RequestProcessor


class ClientThread(threading.Thread):
    def __init__(self, conn, addr, debug, working_dir):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.debug = debug
        self.working_dir = working_dir

    def run(self):

        request_data = list()

        if self.debug:
            print("\nNew request from %s" % str(self.addr))

        self.conn.setblocking(False)
        while True:
            try:
                received_data = self.conn.recv(1024)
            except socket.timeout:
                print("Unable to read request from client. Timed out.")
                break
            except BlockingIOError:
                continue

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
                print("[%s] %s %s %s from: %s" % (
                date_time_now, request.method, request.uri, response.status_code, str(self.addr)))

            try:
                self.conn.sendall(response.construct_response(debug=self.debug))
            except BrokenPipeError:
                print("Client timed out")
            else:
                self.conn.close()

            break


class SocketServer(object):
    def __init__(self, host, port, working_dir, debug=False):
        self.host = host
        self.port = port
        self.working_dir = working_dir
        self.debug = debug
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run_server(self):

        binded = False

        for retry in range(4):
            try:
                self.listener.bind((self.host, self.port))
                binded = True
                break
            except OSError:
                print("Port in use. Retrying...")
                sleep(5)
                continue

        if not binded:
            print("Cannot connect to port. Exiting")
            return

        threads = list()

        try:

            # no. of unaccepted connections that the system will allow before refusing new connections
            self.listener.listen(5)

            print("HTTP Server is listening at %s" % self.port)
            print("Quit the server with CTRL-BREAK")

            while True:
                conn, addr = self.listener.accept()
                client_thread = ClientThread(conn, addr, debug=self.debug, working_dir=self.working_dir)
                client_thread.start()
                threads.append(client_thread)

        except InterruptedError:
            print("Interruption error while accepting connection")
        except KeyboardInterrupt:
            print("Exiting server")
        except OSError as e:
            print("Internal error: %s" % e)
        finally:

            for thread in threads:
                thread.join()

            self.listener.close()


