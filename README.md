# HTTP Server

httpfs is a remote file server manager that sits on top of an HTTP Server Library.
It opens a socket connection and listen for other incoming sockets from HTTP Clients.
The library currently supports GET and POST requests. More features are described below.

> Linux-Distribution only

## Features:

- GET Request
- POST Request
- Request/Response Headers
- Request/Response Body

## Getting Started

There are two ways to run the library, either using the python interpreter
or using the executable from a CLI.
<br>The Python script can be found under httpfs directory "httpfs_lib.py".
<br>The Linux executable can be found under httpfs/dist "httpfs"

### Commands

#### 1. Help commands

They basically show you a help message for each method and the general usage of the
library
```angular2html
./httpfs -h
```

#### 2. PORT definition 

To set the PORT of the server, the following command can be used. If the port is not available, 
the library will try 4 times to connect and at the end will stop. 
```angular2html
./httpfs -p 8080
```

#### 3. Working Directory Definition

There is possibly to set the working directory to perform the requests. The default directory is
the current directory where the library is run. If a request is made outside of the working directory,
a 403 Forbidden is returned to the request.
```angular2html
httpfs -d working_dir/
```
> working_dir is asummed to be a directory where the library is run.

## Additional Features

- Able to handle multiple requests with threads
- Handle GET request to read working directory or a file in the working directory
- Handle POST request to write/create a file
- Respective Error codes are returned to invalid requests
- Content-Type and Content-Disposition is returned to each request

## Build With

- Python 3.5
- Socket built-in library
- PyInstaller (for the executable)

## Additional Notes

Lab Assignment for the Data Communication and Networking class
