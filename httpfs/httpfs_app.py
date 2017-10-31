import argparse
import sys

import os

sys.path.append("../")

from httpfs.http_lib.socket_server import SocketServer


class DirPath(argparse.Action):
    """Expand user- and relative-paths"""
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))


def is_dir(dir_path):
    if not os.path.isdir(dir_path):
        raise argparse.ArgumentTypeError("% is not a directory" % dir_path)
    else:
        return dir_path


def main():
    parser = argparse.ArgumentParser(prog='httpfs', description="httpfs is a simple file server.")

    parser.add_argument("-v", help="Prints debugging messages", dest="verbose", action="store_true")
    parser.add_argument("-p", type=int, default=8080,
                        help="Specifies the port number that the server will listen and serve at. Default is 8080.",
                        dest="PORT")
    parser.add_argument("-d", type=is_dir, default=".", action=DirPath,
                        help="Specifies the directory that the server will use to read/write requested files. "
                             "Default is the current directory when launching the application.",
                        dest="PATH-TO-DIR")

    try:

        args = parser.parse_args()
        dict_args = vars(args)

        SocketServer('', port=dict_args.get("PORT"), working_dir=dict_args.get("PATH-TO-DIR"),
                     debug=dict_args.get("verbose")).run_server()

    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
