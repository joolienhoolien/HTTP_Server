import socket  # noqa: F401
import threading


def start_server(host="localhost", port=4221, concurrent_connections=3):
    server = socket.create_server((host, port))
    server.listen(concurrent_connections)
    return server


def handle_request(client_socket):
    # Open the client connection safely using "with", then reply based on their request, then close the connection.
    with client_socket:
        # if the request has no info past the first /, its 200, otherwise its 404
        data = client_socket.recv(1024)
        request = data.decode("utf-8")

        headers = parse_headers(request)

        # GET request
        if headers["GET"]:
            endpoint = headers["GET"]
            protocol = headers["Protocol"]

            # No request header
            if endpoint == "/" and protocol.startswith("HTTP/1.1"):
                response = "HTTP/1.1 200 OK\r\n\r\n"

            # echo returns the parameter it is sent
            elif endpoint.startswith("/echo/") and protocol.startswith("HTTP/1.1"):
                parameter = endpoint.replace("/echo/", "")
                response = (f"HTTP/1.1 200 OK\r\n\r\n"
                            f"Content-Type: text/plain\r\n\r\n"
                            f"Content-Length: {len(parameter)}\r\n\r\n"
                            f"{parameter}\r\n\r\n")

            # user-agent
            elif endpoint.startswith("/user-agent") and protocol.startswith("HTTP/1.1"):
                user_agent = headers["User-Agent"]
                response = (f"HTTP/1.1 200 OK\r\n\r\n"
                            f"Content-Type: text/plain\r\n\r\n"
                            f"Content-Length: {len(user_agent)}\r\n\r\n"
                            f"{user_agent}\r\n\r\n")

            #Request a file
            elif endpoint.startswith("/files/") and protocol.startswith("HTTP/1.1"):
                filename = endpoint.replace("/files/", "")

            else:
                response = "HTTP/1.1 404 OK\r\n\r\n"

        # Not handled CRUD
        else:
            response = "HTTP/1.1 404 OK\r\n\r\n"
        print(response)
        # Respond to client
        client_socket.sendall(response.encode("utf-8"))


def parse_headers(request: str):
    headers_dict = {}
    for header in request.split("\r\n"):
        h_split = header.split(" ")

        #Normal header such as "Connection" : "keep-alive"
        if len(h_split) == 2:
            headers_dict[h_split[0].replace(":", "")] = h_split[1]

        # ex: GET /user-agent HTTP/1.1
        elif len(h_split) == 3:
            headers_dict[h_split[0].replace(":", "")] = h_split[1]
            headers_dict["Protocol"] = h_split[2]
    return headers_dict


def main():
    #Create the server on machine. This can open up to allow requests.
    server_socket = start_server()

    while True:
        #Accept a call from outside the server. Save the other machine so we can reply with an HTTP code
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_request, args=(client_socket,)).start()




if __name__ == "__main__":
    main()
