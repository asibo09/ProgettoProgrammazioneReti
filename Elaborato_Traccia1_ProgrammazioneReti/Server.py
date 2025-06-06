
import sys
import os
import mimetypes
from socket import * 
from datetime import datetime

serverPort = 8080
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(1)
print('Il web server � attivo su http://localhost:' + str(serverPort))

# Cartella da cui servire i file
www_dir = os.path.join(os.getcwd(), "www")

while True:
    print('In attesa di richieste...')
    connectionSocket, addr = serverSocket.accept()

    try:
        message = connectionSocket.recv(1024).decode()
        if not message:
            connectionSocket.close()
            continue

        method, path, *_ = message.split()
        if method != 'GET':
            connectionSocket.close()
            continue

        if path == "/":
            path = "/index.html"

        filepath = os.path.normpath(os.path.join(www_dir, path.lstrip("/")))

        # Protezione contro accessi non autorizzati
        if not filepath.startswith(www_dir):
            raise IOError("Tentativo di accesso non autorizzato")

        if os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                content = f.read()

            mime_type, _ = mimetypes.guess_type(filepath)
            mime_type = mime_type or 'application/octet-stream'

            header = f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\n\r\n"
            connectionSocket.send(header.encode())
            connectionSocket.send(content)

            print(f"[{datetime.now()}] GET {path} -> 200")
        else:
            raise IOError("File non trovato")

    except Exception as e:
        error_response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n"
        error_response += "<html><body><h1>404 Not Found</h1></body></html>"
        connectionSocket.send(error_response.encode())

        print(f"[{datetime.now()}] GET {path} -> 404")

    finally:
        connectionSocket.close()


