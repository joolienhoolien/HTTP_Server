import os
import socket  # noqa: F401
import threading
from pathlib import Path
import gzip


RESPONSE_CODES = {
    200: "HTTP/1.1 200 OK\r\n\r\n",
    201: "HTTP/1.1 201 Created\r\n\r\n",
    404: "HTTP/1.1 404 Not Found\r\n\r\n"
}

def build_response(code=200, content_type='text/plain', content_length=0, content_encoding=None, body=None):
    response = f"{RESPONSE_CODES[code]}" \
                f"Content-Type: {content_type}\r\n\r\n" \
                f"Content-Length: {content_length}\r\n\r\n"
    if content_encoding:
        response += f"Content-Encoding: {content_encoding}\r\n\r\n"
    if body:
        response += f"{body}\r\n\r\n"
    return response

def parse_headers(request):
    headers_dict = {}
    for header in request.split("\r\n"):
        h_split = header.split(":", 1)

        #Normal header such as "Connection" : "keep-alive"
        if len(h_split) == 2:
            headers_dict[h_split[0].replace(":", "")] = h_split[1].strip()

        # ex: GET /user-agent HTTP/1.1
        elif len(h_split) == 1:
            h_split = header.split(" ")
            headers_dict[h_split[0].replace(":", "")] = h_split[1].strip()
            headers_dict["Protocol"] = h_split[2].strip()
    return headers_dict


def encode_gzip(data: str):
    data_bytes = data.encode("utf-8")
    return gzip.compress(data_bytes)


class Request:
    #Constants
    ALLOWED_ENCODINGS = ["gzip"]

    def __init__(self, client_socket):
        data = client_socket.recv(4096)
        print(f"DATA..... {data}")
        request = data.decode()

        head, sep, body = request.partition("\r\n\r\n")
        print(f"BODY..... {body}")

        self.headers = parse_headers(head)
        self.protocol = self.headers["Protocol"]
        self.body = body
        self.encoding = self.resolve_encoding()
        if "GET" in self.headers:
            self.method = "GET"
            self.path = self.headers["GET"]
        elif "POST" in self.headers:
            self.method = "POST"
            self.path = self.headers["POST"]
        else:
            client_socket.sendall(build_response(404).encode("utf-8"))


    def resolve_encoding(self):
        if "Accept-Encoding" in self.headers:
            requested_encodings = list(self.headers["Accept-Encoding"].split(","))
            for encoding in requested_encodings:
                encoding = encoding.strip()
                if encoding in self.ALLOWED_ENCODINGS:
                    return encoding
        return None


    def handle_get(self):
        endpoint = self.headers["GET"]
        protocol = self.headers["Protocol"]

        if endpoint == "/" and protocol.startswith("HTTP/1.1"):
            response = build_response(200, content_encoding=self.encoding)
        elif endpoint.startswith("/echo/") and protocol.startswith("HTTP/1.1"):
            response = self.response_get_echo(endpoint)
        elif endpoint.startswith("/user-agent") and protocol.startswith("HTTP/1.1"):
            response = self.response_get_user_agent()
        elif endpoint.startswith("/files/") and protocol.startswith("HTTP/1.1"):
            response = self.response_get_file()
        else:
            response = build_response(404)
        return response


    def handle_post(self):
        endpoint = self.headers["POST"]
        protocol = self.headers["Protocol"]
        content_type = self.headers["Content-Type"]

        if endpoint.startswith("/files/") and protocol.startswith("HTTP/1.1")\
                and content_type == "application/octet-stream":
                with open("../inbox/"+(Path(endpoint)).stem, mode="w") as file:
                    file.write(self.body)
                    return build_response(201, content_encoding=self.encoding)
        return build_response(404)


    def response_get_echo(self, endpoint):
        parameter = endpoint.replace("/echo/", "")
        if self.encoding == "gzip":
            parameter = encode_gzip(parameter)
        return build_response(200, content_encoding=self.encoding, content_length=len(parameter), body=parameter)


    def response_get_user_agent(self):
        user_agent = (self.headers["User-Agent"])
        return build_response(200, content_length=len(user_agent), content_encoding=self.encoding, body=user_agent)


    def response_get_file(self):
        filepath = Path(os.curdir, ".." + self.path)
        try:
            with open(filepath, "rb") as image_file:
                image_data = image_file.read()
                image_length = len(image_data)
                return build_response(200, content_type="application/octet-stream", content_length=image_length,
                                      content_encoding=self.encoding, body=image_data)
        except FileNotFoundError:
            return build_response(404)


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
            response = build_response(404)
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
