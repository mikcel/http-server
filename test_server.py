from httpfs.http_lib.socket_server import SocketServer

if __name__ == "__main__":
    port = 8007
    SocketServer('', port=port).run_server()
