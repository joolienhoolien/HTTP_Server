# HTTP Server from Scratch!

[HTTP](https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol) is the
protocol that powers the web. 
The code is my own, however it follows a guided outline by codecrafters.

## Requests
- `GET /`
   - Simply returns a `200` response
- `GET /echo/{word}`
   - Returns `200` with {word} as the body
- `GET /files/{filename}`
   - Returns `200` with a binary of the file in files with the name {filename}
      - The only file currently is cat.jpg
   - Returns `404` if file not found
- `GET /user-agent`
   - Returns `200` with the user-agent of the request as the response body
- `POST /files/{filename}`
   - Returns `201` if file was uploaded. Adds file sent in body of POST to "inbox" folder.

## GZIP Compression
Allows for gzip compression in the response body of "echo" endpoint if Accept-Encoding is set to "gzip" in request

## Concurrent Connections
Try connecting with multiple connections simultaneously. Multithreading is implemented up to 3 threads while server is active.

## Libraries
Only uses python native libraries: `os, socket, threading, Path, gzip`