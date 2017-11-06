
__author__ = "Celine Mikiel Yohann"
__id__ = "40009948"

import socket
import threading
import logging
from datetime import datetime
from time import sleep

import sys

from httpfs.http_lib.http_request import HTTPRequest
from httpfs.http_lib.request_processor import RequestProcessor

lock = threading.Lock()


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

        while True:

            # Get all data from the client
            try:
                received_data = self.conn.recv(8092)
            except socket.timeout:
                print("Unable to read request from client. Timed out.")
                break
            except BlockingIOError:
                continue

            # If no data sent, leave the loop
            if not received_data:
                break
            else:
                request_data.append(received_data.decode())

            request_data = ''.join(request_data)

            logging.info("====PARSING REQUEST====")

            # Create a request
            request = HTTPRequest(raw_request_data=request_data)

            logging.info("====PROCESSING REQUEST====")

            # Process the request
            response = RequestProcessor(request=request, working_dir=self.working_dir).process_request()

            logging.info("====SENDING RESPONSE====")

            # Special output if in debug mode
            if not self.debug:
                date_time_now = datetime.now().strftime("%d/%b/%Y %H:%M:%S")
                print("[%s] %s %s %s:%s from: %s" % (date_time_now, request.method, request.uri,
                                                     response.status_code, response.map_status_code(),
                                                     str(self.addr)))

            try:
                # Send response back to client
                self.conn.sendall(response.construct_response())
            except BrokenPipeError:
                logging.error("Client timed out")
            except BlockingIOError:
                logging.error("Connection blocked")
                pass
            except Exception as e:
                logging.error(e)
            finally:
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

        # Use logging to stdout if verbose activated
        if self.debug:
            logging.basicConfig(stream=sys.stdout, format='%(message)s', level=logging.INFO)
        else:
            logging.getLogger().disabled = True

        # Try to connect to port if not available
        for retry in range(4):
            try:
                self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

            print("Working Dir: %s" % self.working_dir)

            print("HTTP Server is listening at %s" % self.port)
            print("Quit the server with CTRL-BREAK")

            # Listen to incoming connection
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

            # Join all threads before leaving
            for thread in threads:
                thread.join()

            self.listener.close()
