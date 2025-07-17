import socket  # noqa: F401


def build_http_response():
    pass


def main():
    #Create the server on machine. This can open up to allow requests.
    server_socket = socket.create_server(("localhost", 4221))

    #Accept a call from outside the server. Save the other machine so we can reply with an HTTP code
    client_socket, addr = server_socket.accept()
    with client_socket:
        #if the request has no info past the first /, its 200, otherwise its 404
        data = client_socket.recv(1024)
        request = data.decode()

        #Parse
        if request.startswith("GET / HTTP/1.1"):
            response = "HTTP/1.1 200 OK\r\n\r\n"
        else:
            response = "HTTP/1.1 404 OK\r\n\r\n"
        client_socket.sendall(response.encode())


if __name__ == "__main__":
    main()
