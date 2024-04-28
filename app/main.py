import socket
from threading import Thread
import sys
import os


def get_file_data(file):
    os.chdir(sys.argv[2])
    contents = ""
    files = os.listdir()
    if file in files:
        with open(file, "r") as f:
            contents = f.read()
    return contents


def write_to_file(file, data):
    os.chdir(sys.argv[2])
    with open(file, "w") as f:
        f.writelines(data)


def get_response(request, encoding):
    request = request.decode(encoding).split("\r\n")

    path = request[0].split(" ")[1]
    user_agent = request[2][12:]
    method = request[0].split(" ")[0]

    if method == "GET":
        if path.startswith("/echo/"):
            path = path[6:]
            response = f"HTTP/1.1 200 OK \r\nContent-Type: text/plain \r\nContent-Length: {len(path)}\r\n\n{path}\r\n\r\n"
        elif path == "/":
            response = f"HTTP/1.1 200 OK \r\n\r\n"
        elif path == "/user-agent":
            response = f"HTTP/1.1 200 OK \r\nContent-Type: text/plain \r\nContent-Length:{len(user_agent)}\r\n\n{user_agent}\r\n\r\n"
        elif path.startswith("/files/"):
            file_path = path[7:]
            contents = get_file_data(file_path)
            if contents:
                response = f"HTTP/1.1 200 OK \r\nContent-Type: application/octet-stream\r\nContent-Length:{len(contents)}\r\n\n{contents}\r\n\r\n"
            else:
                response = "HTTP/1.1 404 NOT FOUND\r\n\r\n"
        else:
            response = "HTTP/1.1 404 NOT FOUND\r\n\r\n"
    elif method == "POST":
        data = request[5:]
        file_path = path[7:]
        write_to_file(file_path, data)
        response = "HTTP/1.1 201\r\n\r\n"
    else:
        response = "HTTP/1.1 404 NOT FOUND\r\n\r\n"
    return response.encode(encoding)


def server_task(conn, add, encoding):
    with conn:
        request = conn.recv(1024)
        if not request:
            return
        response = get_response(request, encoding)
        conn.sendall(response)


def main():
    add = ("localhost", 4221)
    server_socket = socket.create_server(add, reuse_port=True)

    print(f"The server is listening on port : {add[1]} at address : {add[0]}")

    server_socket.listen()

    encoding = "utf-8"
    while True:
        conn, address = server_socket.accept()
        thread = Thread(target=server_task, args=(conn, address, encoding))
        thread.start()


if __name__ == "__main__":
    main()
