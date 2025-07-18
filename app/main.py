import socket
import threading
from request import Request


def start_server(host="localhost", port=4221, concurrent_connections=3):
    server = socket.create_server((host, port), )
    server.listen(concurrent_connections)
    return server


def handle_request(client_socket):
    with client_socket:
        request = Request(client_socket)
        if request.method == "GET":
            response = request.handle_get()
        elif request.method == "POST":
            response = request.handle_post()
        else:
            response = request.build_response(404)
        client_socket.sendall(response.encode("utf-8"))


def main():
    #Create the server on machine. This can open up to allow requests.
    server_socket = start_server()

    while True:
        #Accept a call from outside the server. Save the other machine so we can reply with an HTTP code
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_request, args=(client_socket,)).start()


if __name__ == "__main__":
    main()
